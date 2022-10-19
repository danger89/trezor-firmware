# This file is part of the Trezor project.
#
# Copyright (C) 2012-2019 SatoshiLabs and contributors
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the License along with this library.
# If not, see <https://www.gnu.org/licenses/lgpl-3.0.html>.

from typing import TYPE_CHECKING
from . import exceptions, messages
from .messages import ZcashSignatureType as SigType
from .tools import expect

if TYPE_CHECKING:
    from typing import Generator
    from .client import TrezorClient


@expect(messages.ZcashFullViewingKey, field="fvk")
def get_fvk(client: TrezorClient, z_address_n: list[int], coin_name: str = "Zcash") -> str:
    """
    Returns Zcash Orchard Full Viewing Key in hexadecimal representation.
    Acording to the https://zips.z.cash/protocol/protocol.pdf § 5.6.4.4
    key components are chained in the following order
    ak (32 bytes) || nk (32 bytes) || rivk (32 bytes)
    """
    return client.call(
        messages.ZcashGetFullViewingKey(
            z_address_n=z_address_n,
            coin_name=coin_name,
        )
    )


@expect(messages.ZcashIncomingViewingKey, field="ivk")
def get_ivk(client: TrezorClient, z_address_n: list[int], coin_name: str = "Zcash") -> str:
    """
    Returns Zcash Orchard Incoming Viewing Key in hexadecimal representation.
    Acording to the https://zips.z.cash/protocol/protocol.pdf § 5.6.4.3
    key components are chained in the following order
    dk (32 bytes) || ivk (32 bytes)
    """
    return client.call(
        messages.ZcashGetIncomingViewingKey(
            z_address_n=z_address_n,
            coin_name=coin_name,
        )
    )


@expect(messages.ZcashAddress, field="address")
def get_address(
    client,
    t_address_n: list[int] | None = None,
    z_address_n: list[int] | None = None,
    diversifier_index: int = 0,
    show_display: bool = False,
    coin_name: str = "Zcash",
):
    """
    Returns a Zcash address.
    """
    return client.call(
        messages.ZcashGetAddress(
            t_address_n=t_address_n or [],
            z_address_n=z_address_n or [],
            diversifier_index=diversifier_index,
            show_display=show_display,
            coin_name=coin_name,
        )
    )


EMPTY_ANCHOR = bytes.fromhex("ae2935f1dfd8a24aed7c70df7de3a668eb7a49b1319880dde2bbd9031ae5d82f")


def sign_tx(
    client,
    inputs: list[messages.TxInput | messages.ZcashOrchardInput],
    outputs: list[messages.TxOutput | messages.ZcashOrchardOutput],
    coin_name: str = "Zcash",
    version_group_id: int = 0x26A7270A,  # protocol spec §7.1.2
    branch_id: int = 0xC2D6D0B4,  # https://zips.z.cash/zip-0252
    expiry: int = 0,
    account: int = 0,
    anchor: bytes = EMPTY_ANCHOR,
    verbose: bool = False,
) -> Generator[None, bytes, (dict[int, bytes], bytes)]:
    """
    Sign a Zcash transaction.

    Parameters:
    -----------
    inputs: transaction inputs
    outputs: transaction outputs
    coin_name: coin name (currently "Zcash" or "Zcash Testnet")
    version_group_id: 0x26A7270A by default
    branch_id: 0xC2D6D0B4 by default
    expiry: 0 by default
    account: account number, from which is spent
        third digit of ZIP-32 path. 0 by default
    anchor: Orchard anchor
    verbose: log protocol transctiption into stdout

    Example:
    --------
    protocol = zcash.sign_tx(
        inputs=[
            TxInput(...)
        ],
        outputs=[
            TxOutput(...),
            ZcashOrchardOutput(...),
        ]
        anchor=bytes.fromhex(...),
        verbose=True,
    )
    shielding_seed = next(protocol)
    ... # run Orchard prover in parallel here
    sighash = next(protocol)
    signatures, serialized_tx = next(protocol)
    """

    def log(*args, **kwargs):
        if verbose:
            print(*args, **kwargs)

    t_inputs = [x for x in inputs if isinstance(x, messages.TxInput)]
    t_outputs = [x for x in outputs if isinstance(x, messages.TxOutput)]
    o_inputs = [x for x in inputs if isinstance(x, messages.ZcashOrchardInput)]
    o_outputs = [x for x in outputs if isinstance(x, messages.ZcashOrchardOutput)]

    msg = messages.SignTx(
        inputs_count=len(t_inputs),
        outputs_count=len(t_outputs),
        coin_name=coin_name,
        version=5,
        version_group_id=version_group_id,
        branch_id=branch_id,
        expiry=expiry,
        orchard_inputs_count=len(o_inputs),
        orchard_outputs_count=len(o_outputs),
        orchard_anchor=anchor,
        account=account,
    )

    actions_count = (
        max(len(o_outputs), len(o_inputs), 2)
        if len(o_outputs) + len(o_inputs) > 0
        else 0)

    serialized_tx = b""

    signatures = {
        SigType.TRANSPARENT: [None] * len(t_inputs),
        SigType.ORCHARD_SPEND_AUTH:  dict(),
    }

    log("T <- sign tx")
    res = client.call(msg)

    R = messages.RequestType
    while isinstance(res, messages.TxRequest):
        # If there's some part of signed transaction, let's add it
        if res.serialized:
            if res.serialized.serialized_tx:
                log("T -> serialized tx ({} bytes)".format(len(res.serialized.serialized_tx)))
                serialized_tx += res.serialized.serialized_tx

            if res.serialized.signature_index is not None:
                idx = res.serialized.signature_index
                sig = res.serialized.signature
                sig_type = res.serialized.signature_type
                if sig_type == SigType.TRANSPARENT:
                    log(f"T -> t signature {idx}")
                    if signatures[sig_type][idx] is not None:
                        raise ValueError(f"Transparent signature for index {idx} already filled")
                elif sig_type == SigType.ORCHARD_SPEND_AUTH:
                    log(f"T -> o signature {idx}")
                    if signatures[sig_type].get(idx) is not None:
                        raise ValueError(f"Orchard signature for index {idx} already filled")
                    if idx >= actions_count:
                        raise IndexError(f"Orchard signature index out of range: {idx}")
                else:
                    raise ValueError(f"Unknown signature type: {sig_type}.")
                signatures[sig_type][idx] = sig

            if res.serialized.zcash_shielding_seed is not None:
                log("T -> shielding seed")
                yield res.serialized.zcash_shielding_seed

            if res.serialized.tx_sighash is not None:
                log("T -> sighash")
                yield res.serialized.tx_sighash

        log("")

        if res.request_type == R.TXFINISHED:
            break

        elif res.request_type == R.TXINPUT:
            log("T <- t input", res.details.request_index)
            msg = messages.TransactionType()
            msg.inputs = [t_inputs[res.details.request_index]]
            res = client.call(messages.TxAck(tx=msg))

        elif res.request_type == R.TXOUTPUT:
            log("T <- t output", res.details.request_index)
            msg = messages.TransactionType()
            msg.outputs = [t_outputs[res.details.request_index]]
            res = client.call(messages.TxAck(tx=msg))

        elif res.request_type == R.TXORCHARDINPUT:
            txi = o_inputs[res.details.request_index]
            log("T <- o input ", res.details.request_index)
            res = client.call(txi)

        elif res.request_type == R.TXORCHARDOUTPUT:
            txo = o_outputs[res.details.request_index]
            log("T <- o output", res.details.request_index)
            res = client.call(txo)

        elif res.request_type == R.NO_OP:
            res = client.call(messages.ZcashAck())

        else:
            raise ValueError("unexpected request type: {}".format(res.request_type))

    if not isinstance(res, messages.TxRequest):
        raise exceptions.TrezorException("Unexpected message")

    yield (signatures, serialized_tx)
