from storage import cache, common, device
from trezor import config


def wipe() -> None:
    config.wipe()
    cache.clear_all()


def reset() -> None:
    """
    Wipes storage but keeps the device id unchanged.
    """
    device_id = device.get_device_id()
    wipe()
    common.set(common.APP_DEVICE, device.DEVICE_ID, device_id.encode(), public=True)
