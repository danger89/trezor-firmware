import gc
from micropython import const
from typing import TYPE_CHECKING

from trezor import log
from trezor.crypto.hashlib import blake2b
from trezor.enums import RequestType, ZcashSignatureType
from trezor.messages import TxRequest, ZcashAck, ZcashOrchardInput, ZcashOrchardOutput
from trezor.wire import DataError

from apps.bitcoin.sign_tx import helpers
from apps.common.paths import HARDENED

from .. import unified
from ..hasher import ZcashHasher
from ..layout import ConfirmOrchardInputsCountOverThreshold
from .accumulator import MessageAccumulator
from .crypto import builder, redpallas
from .crypto.address import Address
from .crypto.note import Note
from .debug import watch_gc_async
from .keychain import OrchardKeychain
from .random import BundleShieldingRng

if TYPE_CHECKING:
    from typing import Awaitable, List
    from apps.common.coininfo import CoinInfo
    from apps.bitcoin.sign_tx.tx_info import TxInfo
    from .crypto.keys import FullViewingKey
    from ..approver import ZcashApprover
    from .random import ActionShieldingRng


OVERWINTERED = const(0x8000_0000)
FLAGS = const(0b0000_0011)  # spends enbled and output enabled
MAX_SILENT_ORCHARD_INPUTS = const(8)


def skip_if_empty(func):
    """
    A function decorated by this will not be evaluated,
    if the Orchard bundle is impty.
    """

    async def wrapper(self):
        if self.actions_count == 0:
            return
        else:
            await func(self)

    return wrapper


class OrchardSigner:
    def __init__(
        self,
        tx_info: TxInfo,
        seed: bytes,
        approver: ZcashApprover,
        coin: CoinInfo,
        tx_req: TxRequest,
    ) -> None:
        assert tx_req.serialized is not None  # typing

        self.inputs_count = tx_info.tx.orchard_inputs_count
        self.outputs_count = tx_info.tx.orchard_outputs_count

        if self.inputs_count + self.outputs_count > 0:
            self.actions_count = max(
                2,  # minimal required amount of actions
                self.inputs_count,
                self.outputs_count,
            )
        else:
            self.actions_count = 0

        if self.actions_count == 0:
            return  # no need to initialize other attributes

        self.tx_info = tx_info
        self.keychain = OrchardKeychain.from_seed_and_coin(seed, coin)
        self.approver = approver
        self.coin = coin
        self.tx_req = tx_req
        assert isinstance(tx_info.sig_hasher, ZcashHasher)
        self.sig_hasher: ZcashHasher = tx_info.sig_hasher

        account = tx_info.tx.account
        assert account is not None  # typing
        key_path = [
            32 | HARDENED,  # ZIP-32 constant
            coin.slip44 | HARDENED,  # purpose
            account | HARDENED,  # account
        ]
        self.key_node = self.keychain.derive(key_path)

        self.msg_acc = MessageAccumulator(
            self.keychain.derive_slip21(
                [b"Zcash Orchard", b"Message Accumulator"],
            ).key()
        )

        self.rng = None

    @skip_if_empty
    async def process_inputs(self) -> None:
        await self.check_orchard_inputs_count()
        for i in range(self.inputs_count):
            txi = await self.get_input(i)
            self.msg_acc.xor_message(txi, i)  # add message to the accumulator
            self.approver.add_orchard_input(txi)

    def check_orchard_inputs_count(self) -> Awaitable[None]:  # type: ignore [awaitable-is-generator]
        if self.inputs_count > MAX_SILENT_ORCHARD_INPUTS:
            yield ConfirmOrchardInputsCountOverThreshold(self.inputs_count)

    @skip_if_empty
    async def approve_outputs(self) -> None:
        for i in range(self.outputs_count):
            txo = await self.get_output(i)
            self.msg_acc.xor_message(txo, i)  # add message to the accumulator
            if output_is_internal(txo):
                self.approver.add_orchard_change_output(txo)
            else:
                await self.approver.add_orchard_external_output(txo)

    @skip_if_empty
    async def compute_digest(self) -> None:
        # derive shielding seed
        shielding_seed = self.derive_shielding_seed()
        self.rng = BundleShieldingRng(seed=shielding_seed)

        # send shielded_seed to the host
        assert self.tx_req.serialized is not None  # typing
        self.tx_req.serialized.zcash_shielding_seed = shielding_seed
        await self.release_serialized()

        # shuffle inputs
        inputs: List[int | None] = list(range(self.inputs_count))
        assert inputs is not None  # typing
        pad(inputs, self.actions_count)
        self.rng.shuffle_inputs(inputs)
        self.shuffled_inputs = inputs

        # shuffle_outputs
        outputs: List[int | None] = list(range(self.outputs_count))
        assert outputs is not None  # typing
        pad(outputs, self.actions_count)
        self.rng.shuffle_outputs(outputs)
        self.shuffled_outputs = outputs

        # precompute Full Viewing Key
        fvk = self.key_node.full_viewing_key()

        # shield and hash actions
        log.info(__name__, "start shielding")
        for i, (j, k) in enumerate(
            zip(
                self.shuffled_inputs,
                self.shuffled_outputs,
            )
        ):
            gc.collect()
            log.info(__name__, "shielding action %d (io: %s %s)", i, str(j), str(k))
            rng_i = self.rng.for_action(i)
            input_info = await self.build_input_info(j, fvk, rng_i)
            output_info = await self.build_output_info(k, fvk, rng_i)

            action = builder.build_action(input_info, output_info, rng_i)
            self.sig_hasher.orchard.add_action(action)

        log.info(__name__, "end shielding")

        # check that message accumulator is empty
        self.msg_acc.check()

        # hash orchard footer
        assert self.tx_info.tx.orchard_anchor is not None  # typing
        self.sig_hasher.orchard.finalize(
            flags=FLAGS,
            value_balance=self.approver.orchard_balance,
            anchor=self.tx_info.tx.orchard_anchor,
        )

    def derive_shielding_seed(self) -> bytes:
        assert self.tx_info.tx.orchard_anchor is not None  # typing
        ss_slip21 = self.keychain.derive_slip21(
            [b"Zcash Orchard", b"bundle_shielding_seed"],
        ).key()
        ss_hasher = blake2b(personal=b"TrezorShieldSeed", outlen=32)
        ss_hasher.update(self.sig_hasher.header.digest())
        ss_hasher.update(self.sig_hasher.transparent.digest())
        ss_hasher.update(self.msg_acc.state)
        ss_hasher.update(self.tx_info.tx.orchard_anchor)
        ss_hasher.update(ss_slip21)
        return ss_hasher.digest()

    @watch_gc_async
    async def build_input_info(
        self,
        index: int | None,
        fvk: FullViewingKey,
        rng: ActionShieldingRng,
    ) -> builder.InputInfo:
        if index is None:
            return builder.InputInfo.dummy(rng)

        txi = await self.get_input(index)
        self.msg_acc.xor_message(txi, index)  # remove message from the accumulator

        note = Note.from_message(txi)
        return builder.InputInfo(note, fvk)

    @watch_gc_async
    async def build_output_info(
        self,
        index: int | None,
        fvk: FullViewingKey,
        rng: ActionShieldingRng,
    ) -> builder.OutputInfo:
        if index is None:
            return builder.OutputInfo.dummy(rng)

        txo = await self.get_output(index)
        self.msg_acc.xor_message(txo, index)  # remove message from the accumulator

        if output_is_internal(txo):
            fvk = fvk.internal()
            address = fvk.address(0)
        else:
            assert txo.address is not None  # typing
            receivers = unified.decode_address(txo.address, self.coin)
            address = receivers.get(unified.Typecode.ORCHARD)
            if address is None:
                raise DataError("Address has not an Orchard receiver.")
            address = Address.from_bytes(address)

        ovk = fvk.outgoing_viewing_key()
        return builder.OutputInfo(ovk, address, txo.amount, txo.memo)

    @skip_if_empty
    @watch_gc_async
    async def sign_inputs(self) -> None:
        sighash = self.sig_hasher.signature_digest()
        self.set_sighash(sighash)
        sig_type = ZcashSignatureType.ORCHARD_SPEND_AUTH
        ask = self.key_node.spend_authorizing_key()
        assert self.rng is not None
        for i, j in enumerate(self.shuffled_inputs):
            if j is None:
                continue
            rng = self.rng.for_action(i)
            rsk = redpallas.randomize(ask, rng.alpha())
            signature = redpallas.sign_spend_auth(rsk, sighash, rng)
            await self.set_serialized_signature(i, signature, sig_type)

    def set_sighash(self, sighash: bytes) -> None:
        assert self.tx_req.serialized is not None
        self.tx_req.serialized.tx_sighash = sighash

    async def set_serialized_signature(
        self, i: int, signature: bytes, sig_type: ZcashSignatureType
    ) -> None:
        assert self.tx_req.serialized is not None
        s = self.tx_req.serialized
        if s.signature_index is not None:
            await self.release_serialized()
        s.signature_index = i
        s.signature = signature
        s.signature_type = sig_type

    def get_input(self, i) -> Awaitable[ZcashOrchardInput]:  # type: ignore [awaitable-is-generator]
        self.tx_req.request_type = RequestType.TXORCHARDINPUT
        assert self.tx_req.details  # typing
        self.tx_req.details.request_index = i
        txi = yield ZcashOrchardInput, self.tx_req
        helpers._clear_tx_request(self.tx_req)
        return txi

    def get_output(self, i: int) -> Awaitable[ZcashOrchardOutput]:  # type: ignore [awaitable-is-generator]
        self.tx_req.request_type = RequestType.TXORCHARDOUTPUT
        assert self.tx_req.details is not None  # typing
        self.tx_req.details.request_index = i
        txo = yield ZcashOrchardOutput, self.tx_req
        helpers._clear_tx_request(self.tx_req)
        return txo

    def release_serialized(self) -> Awaitable[None]:  # type: ignore [awaitable-is-generator]
        self.tx_req.request_type = RequestType.NO_OP
        res = yield ZcashAck, self.tx_req
        helpers._clear_tx_request(self.tx_req)
        return res


def pad(items: list[int | None], target_length: int) -> None:
    items.extend((target_length - len(items)) * [None])


def output_is_internal(txo: ZcashOrchardOutput) -> bool:
    return txo.address is None
