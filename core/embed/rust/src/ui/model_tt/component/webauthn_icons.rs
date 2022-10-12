//! generated from webauthn_icons.rs.mako
//! (by running `make templates` in `core`)
//! do not edit manually!

const ICON_AWS: &[u8] = include_res!("model_tt/res/webauthn/icon_aws.toif");
const ICON_BINANCE: &[u8] = include_res!("model_tt/res/webauthn/icon_binance.toif");
const ICON_BITBUCKET: &[u8] = include_res!("model_tt/res/webauthn/icon_bitbucket.toif");
const ICON_BITFINEX: &[u8] = include_res!("model_tt/res/webauthn/icon_bitfinex.toif");
const ICON_BITWARDEN: &[u8] = include_res!("model_tt/res/webauthn/icon_bitwarden.toif");
const ICON_CLOUDFLARE: &[u8] = include_res!("model_tt/res/webauthn/icon_cloudflare.toif");
const ICON_COINBASE: &[u8] = include_res!("model_tt/res/webauthn/icon_coinbase.toif");
const ICON_DASHLANE: &[u8] = include_res!("model_tt/res/webauthn/icon_dashlane.toif");
const ICON_DROPBOX: &[u8] = include_res!("model_tt/res/webauthn/icon_dropbox.toif");
const ICON_DUO: &[u8] = include_res!("model_tt/res/webauthn/icon_duo.toif");
const ICON_FACEBOOK: &[u8] = include_res!("model_tt/res/webauthn/icon_facebook.toif");
const ICON_FASTMAIL: &[u8] = include_res!("model_tt/res/webauthn/icon_fastmail.toif");
const ICON_FEDORA: &[u8] = include_res!("model_tt/res/webauthn/icon_fedora.toif");
const ICON_GANDI: &[u8] = include_res!("model_tt/res/webauthn/icon_gandi.toif");
const ICON_GEMINI: &[u8] = include_res!("model_tt/res/webauthn/icon_gemini.toif");
const ICON_GITHUB: &[u8] = include_res!("model_tt/res/webauthn/icon_github.toif");
const ICON_GITLAB: &[u8] = include_res!("model_tt/res/webauthn/icon_gitlab.toif");
const ICON_GOOGLE: &[u8] = include_res!("model_tt/res/webauthn/icon_google.toif");
const ICON_INVITY: &[u8] = include_res!("model_tt/res/webauthn/icon_invity.toif");
const ICON_KEEPER: &[u8] = include_res!("model_tt/res/webauthn/icon_keeper.toif");
const ICON_KRAKEN: &[u8] = include_res!("model_tt/res/webauthn/icon_kraken.toif");
const ICON_LOGIN_GOV: &[u8] = include_res!("model_tt/res/webauthn/icon_login.gov.toif");
const ICON_MICROSOFT: &[u8] = include_res!("model_tt/res/webauthn/icon_microsoft.toif");
const ICON_MOJEID: &[u8] = include_res!("model_tt/res/webauthn/icon_mojeid.toif");
const ICON_NAMECHEAP: &[u8] = include_res!("model_tt/res/webauthn/icon_namecheap.toif");
const ICON_PROTON: &[u8] = include_res!("model_tt/res/webauthn/icon_proton.toif");
const ICON_SLUSHPOOL: &[u8] = include_res!("model_tt/res/webauthn/icon_slushpool.toif");
const ICON_STRIPE: &[u8] = include_res!("model_tt/res/webauthn/icon_stripe.toif");
const ICON_TUTANOTA: &[u8] = include_res!("model_tt/res/webauthn/icon_tutanota.toif");
/// Default icon when app does not have its own
const ICON_WEBAUTHN: &[u8] = include_res!("model_tt/res/webauthn/icon_webauthn.toif");

/// Translates icon name into its data.
/// Returns default `ICON_WEBAUTHN` when the icon is not found or name not
/// supplied.
pub fn get_webauthn_icon_data<T: AsRef<str>>(icon_name: Option<T>) -> &'static [u8] {
    if let Some(icon_name) = icon_name {
        match icon_name.as_ref() {
            "aws" => ICON_AWS,
            "binance" => ICON_BINANCE,
            "bitbucket" => ICON_BITBUCKET,
            "bitfinex" => ICON_BITFINEX,
            "bitwarden" => ICON_BITWARDEN,
            "cloudflare" => ICON_CLOUDFLARE,
            "coinbase" => ICON_COINBASE,
            "dashlane" => ICON_DASHLANE,
            "dropbox" => ICON_DROPBOX,
            "duo" => ICON_DUO,
            "facebook" => ICON_FACEBOOK,
            "fastmail" => ICON_FASTMAIL,
            "fedora" => ICON_FEDORA,
            "gandi" => ICON_GANDI,
            "gemini" => ICON_GEMINI,
            "github" => ICON_GITHUB,
            "gitlab" => ICON_GITLAB,
            "google" => ICON_GOOGLE,
            "invity" => ICON_INVITY,
            "keeper" => ICON_KEEPER,
            "kraken" => ICON_KRAKEN,
            "login.gov" => ICON_LOGIN_GOV,
            "microsoft" => ICON_MICROSOFT,
            "mojeid" => ICON_MOJEID,
            "namecheap" => ICON_NAMECHEAP,
            "proton" => ICON_PROTON,
            "slushpool" => ICON_SLUSHPOOL,
            "stripe" => ICON_STRIPE,
            "tutanota" => ICON_TUTANOTA,
            _ => ICON_WEBAUTHN,
        }
    } else {
        ICON_WEBAUTHN
    }
}
