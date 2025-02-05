from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from trezor.messages import RebootToBootloader
    from typing import NoReturn
    from trezor.wire import Context


async def reboot_to_bootloader(ctx: Context, msg: RebootToBootloader) -> NoReturn:
    import storage.device
    from trezor import io, loop, utils, wire
    from trezor.messages import Success
    from trezor.ui.layouts import confirm_action

    if not storage.device.get_experimental_features():
        raise wire.UnexpectedMessage("Experimental features are not enabled")

    await confirm_action(
        ctx,
        "reboot",
        "Go to bootloader",
        "Do you want to restart Trezor in bootloader mode?",
        hold_danger=True,
        verb="Restart",
    )
    await ctx.write(Success(message="Rebooting"))
    # make sure the outgoing USB buffer is flushed
    await loop.wait(ctx.iface.iface_num() | io.POLL_WRITE)
    utils.reboot_to_bootloader()
    raise RuntimeError
