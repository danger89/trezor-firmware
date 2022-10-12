DEFAULT_ICON = "apps/webauthn/res/icon_webauthn.toif"


class ConfirmInfo:
    def __init__(self) -> None:
        self.app_icon: bytes | None = None  # UI1, TO BE REMOVED
        self.app_icon_name: str | None = None

    def get_header(self) -> str:
        raise NotImplementedError

    def app_name(self) -> str:
        raise NotImplementedError

    def account_name(self) -> str | None:
        return None

    def load_icon(self, rp_id_hash: bytes) -> None:
        from trezor import res
        from apps.webauthn import knownapps

        fido_app = knownapps.by_rp_id_hash(rp_id_hash)

        if fido_app is not None and fido_app.icon_name is not None:
            self.app_icon_name = fido_app.icon_name

            icon_path = f"apps/webauthn/res/icon_{fido_app.icon_name}.toif"
            self.app_icon = res.load(icon_path)  # UI1, TO BE REMOVED
        else:
            self.app_icon_name = None
            self.app_icon = res.load(DEFAULT_ICON)  # UI1, TO BE REMOVED
