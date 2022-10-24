# This file is part of the Trezor project.
#
# Copyright (C) 2012-2019 SatoshiLabs and contributors
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the License along with this library.
# If not, see <https://www.gnu.org/licenses/lgpl-3.0.html>.

import pytest

from trezorlib import ethereum, exceptions
from trezorlib.debuglink import TrezorClientDebugLink as Client
from trezorlib.exceptions import TrezorFailure
from trezorlib.tools import UH_, parse_path

from ...common import COMMON_FIXTURES_DIR, parametrize_using_common_fixtures

SHOW_MORE = (143, 167)

pytestmark = [pytest.mark.altcoin, pytest.mark.ethereum]


@pytest.mark.skip_t1
@parametrize_using_common_fixtures("ethereum/sign_typed_data.json")
def test_ethereum_sign_typed_data(client: Client, parameters, result):
    with client:
        address_n = parse_path(parameters["path"])
        encoded_network_slip44 = UH_(address_n[1])
        if "definitions" in parameters:
            encoded_network_slip44 = parameters["definitions"].get(
                "slip44", encoded_network_slip44
            )

        defs = ethereum.messages.EthereumDefinitions(
            encoded_network=ethereum.get_definition_from_path(
                ethereum.get_network_definition_path(
                    path=COMMON_FIXTURES_DIR / "ethereum" / "definitions-latest",
                    slip44=encoded_network_slip44,
                )
            )
        )

        ret = ethereum.sign_typed_data(
            client,
            address_n,
            parameters["data"],
            metamask_v4_compat=parameters["metamask_v4_compat"],
            definitions=defs,
        )
        assert ret.address == result["address"]
        assert f"0x{ret.signature.hex()}" == result["sig"]


@pytest.mark.skip_t1
def test_ethereum_sign_typed_data_missing_extern_definitions(client: Client):
    path = "m/44'/6060'/0'/0/0"  # GoChain

    with pytest.raises(TrezorFailure, match=r"DataError: Forbidden key path"):
        ethereum.sign_typed_data(
            client,
            parse_path(path),
            {
                "types": {"EIP712Domain": []},
                "primaryType": "EIP712Domain",
                "message": {},
                "domain": {},
            },
            metamask_v4_compat=True,
        )


@pytest.mark.skip_t2
@parametrize_using_common_fixtures("ethereum/sign_typed_data.json")
def test_ethereum_sign_typed_data_blind(client: Client, parameters, result):
    with client:
        address_n = parse_path(parameters["path"])
        encoded_network_slip44 = UH_(address_n[1])
        if "definitions" in parameters:
            encoded_network_slip44 = parameters["definitions"].get(
                "slip44", encoded_network_slip44
            )

        encoded_network = ethereum.get_definition_from_path(
            ethereum.get_network_definition_path(
                path=COMMON_FIXTURES_DIR / "ethereum" / "definitions-latest",
                slip44=encoded_network_slip44,
            )
        )
        ret = ethereum.sign_typed_data_hash(
            client,
            address_n,
            ethereum.decode_hex(parameters["domain_separator_hash"]),
            # message hash is empty for domain-only hashes
            ethereum.decode_hex(parameters["message_hash"])
            if parameters["message_hash"]
            else None,
            encoded_network=encoded_network,
        )
        assert ret.address == result["address"]
        assert f"0x{ret.signature.hex()}" == result["sig"]


@pytest.mark.skip_t2
def test_ethereum_sign_typed_data_blind_missing_extern_definitions(client: Client):
    path = "m/44'/6060'/0'/0/0"  # GoChain

    with pytest.raises(TrezorFailure, match=r"DataError:.*Forbidden key path"):
        ethereum.sign_typed_data_hash(
            client,
            parse_path(path),
            ethereum.decode_hex(
                "0x6192106f129ce05c9075d319c1fa6ea9b3ae37cbd0c1ef92e2be7137bb07baa1"
            ),
            None,
            encoded_network=None,
        )


# Being the same as the first object in ethereum/sign_typed_data.json
DATA = {
    "types": {
        "EIP712Domain": [
            {"name": "name", "type": "string"},
            {"name": "version", "type": "string"},
            {"name": "chainId", "type": "uint256"},
            {"name": "verifyingContract", "type": "address"},
        ],
        "Person": [
            {"name": "name", "type": "string"},
            {"name": "wallet", "type": "address"},
        ],
        "Mail": [
            {"name": "from", "type": "Person"},
            {"name": "to", "type": "Person"},
            {"name": "contents", "type": "string"},
        ],
    },
    "primaryType": "Mail",
    "domain": {
        "name": "Ether Mail",
        "version": "1",
        "chainId": 1,
        "verifyingContract": "0x1e0Ae8205e9726E6F296ab8869160A6423E2337E",
    },
    "message": {
        "from": {"name": "Cow", "wallet": "0xc0004B62C5A39a728e4Af5bee0c6B4a4E54b15ad"},
        "to": {"name": "Bob", "wallet": "0x54B0Fa66A065748C40dCA2C7Fe125A2028CF9982"},
        "contents": "Hello, Bob!",
    },
}


def input_flow_show_more(client: Client):
    """Clicks show_more button wherever possible"""
    yield  # confirm domain
    client.debug.wait_layout()
    client.debug.click(SHOW_MORE)

    # confirm domain properties
    for _ in range(4):
        yield
        client.debug.press_yes()

    yield  # confirm message
    client.debug.wait_layout()
    client.debug.click(SHOW_MORE)

    yield  # confirm message.from
    client.debug.wait_layout()
    client.debug.click(SHOW_MORE)

    # confirm message.from properties
    for _ in range(2):
        yield
        client.debug.press_yes()

    yield  # confirm message.to
    client.debug.wait_layout()
    client.debug.click(SHOW_MORE)

    # confirm message.to properties
    for _ in range(2):
        yield
        client.debug.press_yes()

    yield  # confirm message.contents
    client.debug.press_yes()

    yield  # confirm final hash
    client.debug.press_yes()


def input_flow_cancel(client: Client):
    """Clicks cancelling button"""
    yield  # confirm domain
    client.debug.press_no()


@pytest.mark.skip_t1
def test_ethereum_sign_typed_data_show_more_button(client: Client):
    defs = ethereum.messages.EthereumDefinitions(
        encoded_network=ethereum.get_definition_from_path(
            ethereum.get_network_definition_path(
                path=COMMON_FIXTURES_DIR / "ethereum" / "definitions-latest",
                slip44=60,
            )
        )
    )

    with client:
        client.watch_layout()
        client.set_input_flow(input_flow_show_more(client))
        ethereum.sign_typed_data(
            client,
            parse_path("m/44h/60h/0h/0/0"),
            DATA,
            metamask_v4_compat=True,
            definitions=defs,
        )


@pytest.mark.skip_t1
def test_ethereum_sign_typed_data_cancel(client: Client):
    defs = ethereum.messages.EthereumDefinitions(
        encoded_network=ethereum.get_definition_from_path(
            ethereum.get_network_definition_path(
                path=COMMON_FIXTURES_DIR / "ethereum" / "definitions-latest",
                slip44=60,
            )
        )
    )

    with client, pytest.raises(exceptions.Cancelled):
        client.watch_layout()
        client.set_input_flow(input_flow_cancel(client))
        ethereum.sign_typed_data(
            client,
            parse_path("m/44h/60h/0h/0/0"),
            DATA,
            metamask_v4_compat=True,
            definitions=defs,
        )
