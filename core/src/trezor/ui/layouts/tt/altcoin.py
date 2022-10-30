from typing import TYPE_CHECKING

from trezor import ui, wire
from trezor.enums import ButtonRequestType
from trezor.utils import chunks_intersperse

from ...components.common.confirm import raise_if_cancelled
from ...components.tt.confirm import Confirm, HoldToConfirm
from ...components.tt.scroll import Paginated
from ...components.tt.text import Text
from ...constants.tt import MONO_ADDR_PER_LINE
from ..common import interact

if TYPE_CHECKING:
    from typing import Sequence
    from ..common import ProgressLayout


async def confirm_total_ethereum(
    ctx: wire.GenericContext, total_amount: str, gas_price: str, fee_max: str
) -> None:
    text = Text("Confirm transaction", ui.ICON_SEND, ui.GREEN, new_lines=False)
    text.bold(total_amount)
    text.normal(" ", ui.GREY, "Gas price:", ui.FG)
    text.bold(gas_price)
    text.normal(" ", ui.GREY, "Maximum fee:", ui.FG)
    text.bold(fee_max)
    await raise_if_cancelled(
        interact(ctx, HoldToConfirm(text), "confirm_total", ButtonRequestType.SignTx)
    )


async def confirm_total_ripple(
    ctx: wire.GenericContext,
    address: str,
    amount: str,
) -> None:
    title = "Confirm sending"
    text = Text(title, ui.ICON_SEND, ui.GREEN, new_lines=False)
    text.bold(f"{amount} XRP\n")
    text.normal("to\n")
    text.mono(*chunks_intersperse(address, MONO_ADDR_PER_LINE))

    await raise_if_cancelled(
        interact(ctx, HoldToConfirm(text), "confirm_output", ButtonRequestType.SignTx)
    )


async def confirm_transfer_binance(
    ctx: wire.GenericContext, inputs_outputs: Sequence[tuple[str, str, str]]
) -> None:
    pages: list[ui.Component] = []
    for title, amount, address in inputs_outputs:
        coin_page = Text(title, ui.ICON_SEND, icon_color=ui.GREEN, new_lines=False)
        coin_page.bold(amount)
        coin_page.normal("\nto\n")
        coin_page.mono(*chunks_intersperse(address, MONO_ADDR_PER_LINE))
        pages.append(coin_page)

    pages[-1] = HoldToConfirm(pages[-1])

    await raise_if_cancelled(
        interact(
            ctx, Paginated(pages), "confirm_transfer", ButtonRequestType.ConfirmOutput
        )
    )


async def confirm_decred_sstx_submission(
    ctx: wire.GenericContext,
    address: str,
    amount: str,
) -> None:
    text = Text("Purchase ticket", ui.ICON_SEND, ui.GREEN, new_lines=False)
    text.normal(amount)
    text.normal("\nwith voting rights to\n")
    text.mono(*chunks_intersperse(address, MONO_ADDR_PER_LINE))
    await raise_if_cancelled(
        interact(
            ctx,
            Confirm(text),
            "confirm_decred_sstx_submission",
            ButtonRequestType.ConfirmOutput,
        )
    )


class MoneroKeyImageSyncProgress:
    def __init__(self) -> None:
        ui.backlight_fade(ui.style.BACKLIGHT_DIM)
        ui.display.clear()
        ui.header("Syncing", ui.ICON_SEND, ui.TITLE_GREY, ui.BG, ui.BLUE)
        ui.backlight_fade(ui.style.BACKLIGHT_NORMAL)

    def report(self, value: int, description: str | None = None) -> None:
        ui.display.loader(value, False, 18, ui.WHITE, ui.BG)
        ui.refresh()


def monero_keyimage_sync_progress() -> ProgressLayout:
    return MoneroKeyImageSyncProgress()


class MoneroLiveRefreshProgress:
    def __init__(self) -> None:
        ui.backlight_fade(ui.style.BACKLIGHT_DIM)
        ui.display.clear()
        ui.header("Refreshing", ui.ICON_SEND, ui.TITLE_GREY, ui.BG, ui.BLUE)
        ui.backlight_fade(ui.style.BACKLIGHT_NORMAL)

    def report(self, value: int, description: str | None = None) -> None:
        ui.display.loader(value, True, 18, ui.WHITE, ui.BG)
        ui.display.text_center(
            ui.WIDTH // 2, 145, description or "", ui.NORMAL, ui.FG, ui.BG
        )
        ui.refresh()


def monero_live_refresh_progress() -> ProgressLayout:
    return MoneroLiveRefreshProgress()


class MoneroTransactionProgressInner:
    def __init__(self) -> None:
        ui.backlight_fade(ui.style.BACKLIGHT_DIM)
        ui.display.clear()
        ui.header("Signing transaction", ui.ICON_SEND, ui.TITLE_GREY, ui.BG, ui.BLUE)
        ui.backlight_fade(ui.style.BACKLIGHT_NORMAL)

    def report(self, value: int, description: str | None = None) -> None:
        info = (description or "").split("\n")
        ui.display.loader(value, False, -4, ui.WHITE, ui.BG)
        ui.display.bar(0, ui.HEIGHT - 48, ui.WIDTH, 48, ui.BG)
        ui.display.text_center(ui.WIDTH // 2, 210, info[0], ui.NORMAL, ui.FG, ui.BG)
        if len(info) > 1:
            ui.display.text_center(ui.WIDTH // 2, 235, info[1], ui.NORMAL, ui.FG, ui.BG)
        ui.refresh()


def monero_transaction_progress_inner() -> ProgressLayout:
    return MoneroTransactionProgressInner()
