from typing import TYPE_CHECKING

from trezor.enums import ButtonRequestType
from trezor.ui.layouts import show_warning
from trezor.ui.layouts.recovery import (  # noqa: F401
    request_word_count,
    show_group_share_success,
    show_remaining_shares,
)

from .. import backup_types

if TYPE_CHECKING:
    from typing import Callable
    from trezor.enums import BackupType
    from trezor.wire import GenericContext


async def _confirm_abort(ctx: GenericContext, dry_run: bool = False) -> None:
    from trezor import ui
    from trezor.ui.layouts import confirm_action

    if dry_run:
        await confirm_action(
            ctx,
            "abort_recovery",
            "Abort seed check",
            description="Do you really want to abort the seed check?",
            icon=ui.ICON_WIPE,
            br_code=ButtonRequestType.ProtectCall,
        )
    else:
        await confirm_action(
            ctx,
            "abort_recovery",
            "Abort recovery",
            "All progress will be lost.",
            "Do you really want to abort the recovery process?",
            reverse=True,
            icon=ui.ICON_WIPE,
            br_code=ButtonRequestType.ProtectCall,
        )


async def request_mnemonic(
    ctx: GenericContext, word_count: int, backup_type: BackupType | None
) -> str | None:
    from . import word_validity
    from trezor.ui.layouts.common import button_request
    from trezor.ui.layouts.recovery import request_word

    await button_request(ctx, "mnemonic", ButtonRequestType.MnemonicInput)

    words: list[str] = []
    for i in range(word_count):
        word = await request_word(
            ctx, i, word_count, is_slip39=backup_types.is_slip39_word_count(word_count)
        )
        words.append(word)

        try:
            word_validity.check(backup_type, words)
        except word_validity.AlreadyAdded:
            # show_share_already_added
            await show_warning(
                ctx,
                "warning_known_share",
                "Share already entered,\nplease enter\na different share.",
            )
            return None
        except word_validity.IdentifierMismatch:
            # show_identifier_mismatch
            await show_warning(
                ctx,
                "warning_mismatched_share",
                "You have entered\na share from another\nShamir Backup.",
            )
            return None
        except word_validity.ThresholdReached:
            # show_group_threshold_reached
            await show_warning(
                ctx,
                "warning_group_threshold",
                "Threshold of this\ngroup has been reached.\nInput share from\ndifferent group.",
            )
            return None

    return " ".join(words)


async def show_dry_run_result(
    ctx: GenericContext, result: bool, is_slip39: bool
) -> None:
    from trezor.ui.layouts import show_success

    if result:
        if is_slip39:
            text = "The entered recovery\nshares are valid and\nmatch what is currently\nin the device."
        else:
            text = "The entered recovery\nseed is valid and\nmatches the one\nin the device."
        await show_success(ctx, "success_dry_recovery", text, button="Continue")
    else:
        if is_slip39:
            text = "The entered recovery\nshares are valid but\ndo not match what is\ncurrently in the device."
        else:
            text = "The entered recovery\nseed is valid but does\nnot match the one\nin the device."
        await show_warning(ctx, "warning_dry_recovery", text, button="Continue")


async def show_invalid_mnemonic(ctx: GenericContext, word_count: int) -> None:
    if backup_types.is_slip39_word_count(word_count):
        await show_warning(
            ctx,
            "warning_invalid_share",
            "You have entered\nan invalid recovery\nshare.",
        )
    else:
        await show_warning(
            ctx,
            "warning_invalid_seed",
            "You have entered\nan invalid recovery\nseed.",
        )


async def homescreen_dialog(
    ctx: GenericContext,
    button_label: str,
    text: str,
    subtext: str | None = None,
    info_func: Callable | None = None,
) -> None:
    from .recover import RecoveryAborted
    import storage.recovery as storage_recovery
    from trezor.wire import ActionCancelled
    from trezor.ui.layouts.recovery import continue_recovery

    while True:
        dry_run = storage_recovery.is_dry_run()
        if await continue_recovery(
            ctx, button_label, text, subtext, info_func, dry_run
        ):
            # go forward in the recovery process
            break
        # user has chosen to abort, confirm the choice
        try:
            await _confirm_abort(ctx, dry_run)
        except ActionCancelled:
            pass
        else:
            raise RecoveryAborted
