# Coin and FIDO Definitions

This directory hosts JSON definitions of recognized coins, tokens, and FIDO/U2F apps.

## FIDO

The [`fido/`](fido) subdirectory contains definitons of apps whose logos and
names are shown on Trezor T screen for FIDO/U2F authentication.

Each app must have a single JSON file in the `fido/` subdirectory. Every app must have
its `label` set to the user-recognizable application name. The `u2f` field is a list of
U2F origin hashes, and the `webauthn` field is a list of FIDO2/WebAuthn hostnames for
the app. At least one must be present.

Each app can have an icon. If present, it must be a 128x128 pixels RGBA PNG of the same
name as the corresponding JSON name. If the app does not have an icon, it must instead
have a field `no_icon` set to `true` in the JSON.

## Coins

We currently recognize five categories of coins.

#### `bitcoin`

The [`bitcoin/`](bitcoin) subdirectory contains definitions for Bitcoin and altcoins
based on Bitcoin code.

Each Bitcoin-like coin must have a single JSON file in the `bitcoin/` subdirectory,
and a corresponding PNG image with the same name. The PNG must be 96x96 pixels and
the picture must be a circle suitable for displaying on Trezor T.

Testnet is considered a separate coin, so it must have its own JSON and icon.

We will not support coins that have `address_type` 0, i.e., same as Bitcoin.

#### `eth` and `erc20`

Definitions for Ethereum chains(networks) and tokens(erc20) are split in two parts:
1. built-in definitions - some of the chain and token definitions are built into the firmware
   image. List of built-in chains is stored in [`ethereum/networks.json`](ethereum/networks.json)
   and tokens in [`ethereum/tokens.json`](ethereum/tokens.json).
2. external definitions - external definitions are dynamically generated from multiple
   sources. Whole process is described in separate [document](Ethereum_definitions.md).

If you want to add or update a token definition in Trezor, you need to get your change
to the [Ethereum Lists - tokens](https://github.com/ethereum-lists/tokens) repository first.

For more details see [document](https://docs.trezor.io/trezor-firmware/common/communication/ethereum-definitions-binary-format.html)
about Ethereum definitions.

#### `nem`

The file [`nem/nem_mosaics.json`](nem/nem_mosaics.json) describes NEM mosaics.

#### `misc`

Supported coins that are not derived from Bitcoin, Ethereum or NEM are currently grouped
and listed in separate file [`misc/misc.json`](misc/misc.json). Each coin must also have
an icon in `misc/<short>.png`, where `short` is lowercased `shortcut` field from the JSON.

## Keys

Throughout the system, coins are identified by a _key_ - a colon-separated string
generated from the coin's type and shortcut:

* for Bitcoin-likes, key is `bitcoin:<shortcut>`
* for Ethereum networks, key is `eth:<shortcut>`
* for ERC20 tokens, key is `erc20:<chain_symbol>:<token_shortcut>`
* for NEM mosaic, key is `nem:<shortcut>`
* for others, key is `misc:<shortcut>`

If a token shortcut has a suffix, such as `CAT (BlockCat)`, the whole thing is part
of the key (so the key is `erc20:eth:CAT (BlockCat)`).

Sometimes coins end up with duplicate keys. We do not allow duplicate symbols
in the built-in data. In such cases, keys are deduplicated by adding:
* first 4 characters of a token address in case of ERC20 tokens, e.g. `erc20:eth:BID:1da0`, or
* a counter at end, e.g.: `erc20:eth:SMT:0`, `erc20:eth:SMT:1`.
Note that the suffix _is not stable_, so these coins can't be reliably uniquely identified.

For Ethereum networks and ERC20 tokens we have a small and stable set of definitions, so key
collisions should not happen.

## Duplicate Detection

**Duplicate symbols are not allowed** in our data. Tokens that have symbol collisions
are removed from the data set before processing. The duplicate status is mentioned
in `support.json` (see below), but it is impossible to override from there.

We try to minimize the occurence of duplicates in built-in tokens, but sometimes its
unavoidable. For Ethereum networks and ERC20 tokens we have a small and stable set
of definitions, so symbol collisions should not happen.

Duplicate detection works as follows:

1. a _symbol_ is split off from the shortcut string. E.g., for `CAT (BlockCat)`, symbol
   is just `CAT`. It is compared, case-insensitive, with other coins (so `WIC` and `WiC`
   are considered the same symbol), and identical symbols are put into a _bucket_.
2. if _all_ coins in the bucket also have a suffix (`CAT (BlockCat)` and `CAT (BitClave)`),
   they are _not_ considered duplicate.
3. if _any_ coin in the bucket does _not_ have a suffix (`MIT` and `MIT (Mychatcoin)`),
   all coins in the bucket are considered duplicate.
4. Duplicate tokens (coins from the `erc20` group) are automatically removed from data.
   Duplicate non-tokens are marked but not removed. For instance, `bitcoin:FTC` (Feathercoin)
   and `erc20:eth:FTC` (FTC) are duplicate, and `erc20:eth:FTC` is removed.
5. If two non-tokens collide with each other, it is an error that fails the CI build.

The file [`duplicity_overrides.json`](duplicity_overrides.json) can override detection
results: keys set to `true` are considered duplicate (in a separate bucket), keys set
to `false` are considered non-duplicate even if auto-detected. This is useful for
whitelisting a supported token explicitly, or blacklisting things that the detection
can't match (for instance "Battle" and "Bitlle" have suffixes, but they are too similar).

External contributors should not make changes to `duplicity_overrides.json`, unless
asked to.

You can use `./tools/cointool.py check -d all` to inspect duplicate detection in detail.


# Wallet URLs

If you want to add a **wallet link**, modify the file [`wallets.json`](wallets.json).

# Support Information

We keep track of support status of each built-in coin over our devices. That is
`trezor1` for Trezor One, `trezor2` for Trezor T, `connect` for [Connect](https://github.com/trezor/connect)
and `suite` for [Trezor Suite](https://suite.trezor.io/). In further description, the word "device"
applies to Connect and Suite as well.

This information is stored in [`support.json`](support.json).
External contributors should not touch this file unless asked to.

Each coin on each device can be in one of four support states:

* **supported** explicitly: coin's key is listed in the device's `supported`
  dictionary. If it's a Trezor device, it contains the firmware version from which
  it is supported. For connect and suite, the value is simply `true`.
* **unsupported** explicitly: coin's key is listed in the device's `unsupported`
  dictionary. The value is a string with reason for not supporting.
  For connect and suite, if the key is not listed at all, it is also considered unsupported.
  ERC20 tokens detected as duplicates are also considered unsupported.
* **unknown**: coin's key is not listed at all.

_Supported_ coins are used in code generation (i.e., included in built firmware).
_Unsupported_ and _unknown_ coins are excluded from code generation.

You can edit `support.json` manually, but it is usually better to use the `support.py` tool.
See [tools docs](../tools) for details.
