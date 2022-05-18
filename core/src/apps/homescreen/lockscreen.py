import storage.cache
from trezor import loop, ui, utils

from . import HomescreenBase


async def lockscreen() -> None:
    from trezor import wire

    from apps.common.request_pin import can_lock_device
    from apps.base import unlock_device

    # Only show the lockscreen UI if the device can in fact be locked.
    if can_lock_device():
        await Lockscreen()
    # Otherwise proceed directly to unlock() call. If the device is already unlocked,
    # it should be a no-op storage-wise, but it resets the internal configuration
    # to an unlocked state.
    try:
        await unlock_device()
    except wire.PinCancelled:
        pass


class Lockscreen(HomescreenBase):
    BACKLIGHT_LEVEL = ui.BACKLIGHT_LOW
    RENDER_SLEEP = loop.SLEEP_FOREVER
    RENDER_INDICATOR = storage.cache.LOCKSCREEN_ON

    def __init__(self, bootscreen: bool = False) -> None:
        if bootscreen:
            self.BACKLIGHT_LEVEL = ui.BACKLIGHT_NORMAL
            self.lock_label = "Not connected"
            self.tap_label = "Tap to connect"
        else:
            self.lock_label = "Locked"
            self.tap_label = "Tap to unlock"

        super().__init__()

    def do_render(self) -> None:
        from trezor import res
        from trezor import ui  # local_cache_global

        if utils.MODEL in ("T",):
            display = ui.display  # local_cache_attribute
            title_grey = ui.TITLE_GREY  # local_cache_attribute
            bg = ui.BG  # local_cache_attribute

            # homescreen with label text on top
            display.text_center(ui.WIDTH // 2, 35, self.label, ui.BOLD, title_grey, bg)
            display.avatar(48, 48, self.get_image(), ui.WHITE, ui.BLACK)

            # lock bar
            display.bar_radius(40, 100, 160, 40, title_grey, bg, 4)
            display.bar_radius(42, 102, 156, 36, bg, title_grey, 4)
            display.text_center(
                ui.WIDTH // 2, 128, self.lock_label, ui.BOLD, title_grey, bg
            )

            # "tap to unlock"
            display.text_center(
                ui.WIDTH // 2 + 10, 220, self.tap_label, ui.BOLD, title_grey, bg
            )
            display.icon(45, 202, res.load(ui.ICON_CLICK), title_grey, bg)
        elif utils.MODEL in ("R",):
            ui.header_warning(self.lock_label)
            icon = "trezor/res/homescreen_model_r.toif"  # 92x92 px
            ui.display.icon(18, 18, ui.res.load(icon), ui.style.FG, ui.style.BG)
            ui.display.text_center(
                ui.WIDTH // 2, 120, self.label, ui.BOLD, ui.FG, ui.BG
            )
        elif utils.MODEL in ("1",):
            ui.header_warning(self.lock_label)
            icon = "trezor/res/homescreen_model_1.toif"  # 64x36 px
            ui.display.icon(33, 14, ui.res.load(icon), ui.style.FG, ui.style.BG)
            ui.display.text_center(ui.WIDTH // 2, 60, self.label, ui.BOLD, ui.FG, ui.BG)

    def on_touch_end(self, _x: int, _y: int) -> None:
        raise ui.Result(None)
