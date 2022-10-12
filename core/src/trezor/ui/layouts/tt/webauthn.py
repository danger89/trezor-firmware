from trezor import ui, wire
from trezor.enums import ButtonRequestType

from ...components.common.confirm import is_confirmed
from ...components.common.webauthn import ConfirmInfo
from ...components.tt.confirm import Confirm, ConfirmPageable, Pageable
from ...components.tt.text import Text
from ...components.tt.webauthn import ConfirmContent
from ..common import interact


async def confirm_webauthn(
    ctx: wire.GenericContext | None,
    info: ConfirmInfo,
) -> bool:
    """Webauthn confirmation for just one specific credential."""
    # There is no choice here, just one page.
    # Converting the `int | None` result into a `bool`.
    result = await confirm_webauthn_choose(ctx, info)
    return result is not None


async def confirm_webauthn_choose(
    ctx: wire.GenericContext | None,
    info: ConfirmInfo,
    pageable: Pageable | None = None,
) -> int | None:
    if pageable is not None:
        confirm: ui.Layout = ConfirmPageable(pageable, ConfirmContent(info))
    else:
        confirm = Confirm(ConfirmContent(info))

    if ctx is None:
        result = is_confirmed(await confirm)
    else:
        result = is_confirmed(
            await interact(ctx, confirm, "confirm_webauthn", ButtonRequestType.Other)
        )

    # NOTE: being compatible with UI2's need to send Optional[int]
    if not result:
        return None
    else:
        return 0 if pageable is None else pageable.page()


async def confirm_webauthn_reset() -> bool:
    text = Text("FIDO2 Reset", ui.ICON_CONFIG)
    text.normal("Do you really want to")
    text.bold("erase all credentials?")
    return is_confirmed(await Confirm(text))
