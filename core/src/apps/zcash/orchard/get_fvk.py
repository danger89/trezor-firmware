from typing import TYPE_CHECKING

from trezor import ui
from trezor.enums import ButtonRequestType
from trezor.messages import ZcashFullViewingKey, ZcashGetFullViewingKey
from trezor.ui.layouts import confirm_action

from apps.common import coininfo

from ..unified import Typecode, encode_fvk
from .keychain import with_keychain

if TYPE_CHECKING:
    from trezor.wire import Context
    from .keychain import OrchardKeychain


@with_keychain
async def get_fvk(
    ctx: Context, msg: ZcashGetFullViewingKey, keychain: OrchardKeychain
) -> ZcashFullViewingKey:
    await require_confirm_export_fvk(ctx)
    fvk = keychain.derive(msg.z_address_n).full_viewing_key()
    receivers = {Typecode.ORCHARD: fvk.to_bytes()}
    coin = coininfo.by_name(msg.coin_name)
    return ZcashFullViewingKey(fvk=encode_fvk(receivers, coin))


async def require_confirm_export_fvk(ctx: Context) -> None:
    await confirm_action(
        ctx,
        "export_full_viewing_key",
        "Confirm export",
        description="Do you really want to export Full Viewing Key?",
        icon=ui.ICON_SEND,
        icon_color=ui.GREEN,
        br_code=ButtonRequestType.SignTx,
    )
