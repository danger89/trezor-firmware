from typing import TYPE_CHECKING

from trezor import wire
from trezor.enums import ButtonRequestType

import trezorui2

from ..common import interact
from . import _RustLayout, is_confirmed

if TYPE_CHECKING:
    from trezor.wire import GenericContext
    from ...components.common.webauthn import ConfirmInfo
    from ...components.tt.confirm import Pageable


async def confirm_webauthn(
    ctx: GenericContext | None,
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
    """Webauthn confirmation when user can choose from more than one credential."""
    # `trezorui2.confirm_webauthn` is expecting a list of tuples
    # (app_name, account_name) to allow for the `pageable` situation.
    # In case the list has only one element, it will not be paginated.
    # Assuming the header and icon are the same for all pages.

    pages: list[tuple[str, str]] = []
    pages.append((info.app_name(), info.account_name() or ""))

    if pageable is not None:
        # Loading all the following app and account names.
        for _ in range(pageable.page_count() - 1):
            pageable.next()
            pages.append((info.app_name(), info.account_name() or ""))

    confirm = _RustLayout(
        trezorui2.confirm_webauthn(
            title=info.get_header().upper(),
            pages=pages,
            icon=info.app_icon_name,
        )
    )

    if ctx is None:
        result = await confirm
    else:
        result = await interact(
            ctx, confirm, "confirm_webauthn", ButtonRequestType.Other
        )

    # Returning None to indicate cancellation, otherwise the index of the
    # chosen page.
    if result is trezorui2.CANCELLED:
        return None
    else:
        assert isinstance(result, int)
        return result


async def confirm_webauthn_reset() -> bool:
    confirm = _RustLayout(
        trezorui2.confirm_action(
            title="FIDO2 RESET",
            action="erase all credentials?",
            description="Do you really want to",
            reverse=True,
        )
    )
    return is_confirmed(await confirm)
