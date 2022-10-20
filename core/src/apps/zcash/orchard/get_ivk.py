from typing import TYPE_CHECKING

from trezor import ui
from trezor.enums import ButtonRequestType
from trezor.messages import ZcashGetIncomingViewingKey, ZcashIncomingViewingKey
from trezor.ui.layouts import confirm_action

from apps.common import coininfo

from ..unified import Typecode, encode_ivk
from .keychain import with_keychain

if TYPE_CHECKING:
    from trezor.wire import Context
    from .keychain import OrchardKeychain


@with_keychain
async def get_ivk(
    ctx: Context, msg: ZcashGetIncomingViewingKey, keychain: OrchardKeychain
) -> ZcashIncomingViewingKey:
    await require_confirm_export_ivk(ctx)
    fvk = keychain.derive(msg.z_address_n).full_viewing_key()
    coin = coininfo.by_name(msg.coin_name)
    receivers = {Typecode.ORCHARD: fvk.incoming_viewing_key()}
    return ZcashIncomingViewingKey(ivk=encode_ivk(receivers, coin))


async def require_confirm_export_ivk(ctx: Context) -> None:
    await confirm_action(
        ctx,
        "export_incoming_viewing_key",
        "Confirm export",
        description="Do you really want to export Incoming Viewing Key?",
        icon=ui.ICON_SEND,
        icon_color=ui.GREEN,
        br_code=ButtonRequestType.SignTx,
    )
