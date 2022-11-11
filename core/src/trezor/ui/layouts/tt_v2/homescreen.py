from typing import Any, Tuple

import storage.cache
import storage.device
from trezor import io, loop, ui, utils

import trezorui2
from apps.base import set_homescreen

from . import RustLayout


class HomescreenBase(RustLayout):
    RENDER_INDICATOR: object | None = None

    def __init__(self, layout: Any) -> None:
        super().__init__(layout=layout)
        self.is_connected = True

    async def __iter__(self) -> Any:
        # We need to catch the ui.Cancelled exception that kills us, because that means
        # that we will need to draw on screen again after restart.
        try:
            return await super().__iter__()
        except ui.Cancelled:
            storage.cache.homescreen_shown = None
            raise

    def _first_paint(self) -> None:
        if storage.cache.homescreen_shown is not self.RENDER_INDICATOR:
            super()._first_paint()
            storage.cache.homescreen_shown = self.RENDER_INDICATOR

        # - RENDER_INDICATOR is set -> USB warning is not displayed
        # - RENDER_INDICATOR is not set -> initially homescreen does not display warning
        # - usb_checker_task only handles state changes
        # Here we need to handle the case when homescreen is started with USB disconnected.
        if not utils.usb_data_connected():
            msg = self.layout.usb_event(False)
            self._paint()
            if msg is not None:
                raise ui.Result(msg)


class Homescreen(HomescreenBase):
    RENDER_INDICATOR = storage.cache.HOMESCREEN_ON

    def __init__(
        self,
        label: str | None,
        notification: str | None,
        notification_is_error: bool,
        hold_to_lock: bool,
    ) -> None:
        level = 1
        if notification is not None:
            notification = notification.rstrip("!")
            if "EXPERIMENTAL" in notification:
                level = 2
            elif notification_is_error:
                level = 0

        skip = storage.cache.homescreen_shown is self.RENDER_INDICATOR
        super().__init__(
            layout=trezorui2.show_homescreen(
                label=label or "My Trezor",
                notification=notification,
                notification_level=level,
                hold=hold_to_lock,
                skip_first_paint=skip,
            ),
        )

    async def usb_checker_task(self) -> None:
        usbcheck = loop.wait(io.USB_CHECK)
        while True:
            is_connected = await usbcheck
            if is_connected != self.is_connected:
                self.is_connected = is_connected
                self.layout.usb_event(is_connected)
                self.layout.paint()
                storage.cache.homescreen_shown = None

    def create_tasks(self) -> Tuple[loop.AwaitableTask, ...]:
        return super().create_tasks() + (self.usb_checker_task(),)


class Lockscreen(HomescreenBase):
    RENDER_INDICATOR = storage.cache.LOCKSCREEN_ON
    BACKLIGHT_LEVEL = ui.BACKLIGHT_LOW

    def __init__(
        self,
        label: str | None,
        bootscreen: bool = False,
    ) -> None:
        self.bootscreen = bootscreen
        if bootscreen:
            self.BACKLIGHT_LEVEL = ui.BACKLIGHT_NORMAL

        skip = (
            not bootscreen and storage.cache.homescreen_shown is self.RENDER_INDICATOR
        )
        super().__init__(
            layout=trezorui2.show_lockscreen(
                label=label or "My Trezor",
                bootscreen=bootscreen,
                skip_first_paint=skip,
            ),
        )

    async def __iter__(self) -> Any:
        result = await super().__iter__()
        if self.bootscreen:
            self.request_complete_repaint()
        return result


class Busyscreen(HomescreenBase):
    RENDER_INDICATOR = storage.cache.BUSYSCREEN_ON

    def __init__(self, delay_ms: int) -> None:
        skip = storage.cache.homescreen_shown is self.RENDER_INDICATOR
        super().__init__(
            layout=trezorui2.show_busyscreen(
                title="PLEASE WAIT",
                description="CoinJoin in progress.\n\nDo not disconnect your\nTrezor.",
                time_ms=delay_ms,
                skip_first_paint=skip,
            )
        )

    async def __iter__(self) -> Any:
        # Handle timeout.
        result = await super().__iter__()
        assert result == trezorui2.CANCELLED
        storage.cache.delete(storage.cache.APP_COMMON_BUSY_DEADLINE_MS)
        set_homescreen()
        return result
