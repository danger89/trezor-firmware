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

import click

from .. import zcash, messages, tools
from . import with_client

@click.group(name="zcash")
def cli():
    """Zcash commands."""

def _parse_network(network):
    return {
        "mainnet": "Zcash",  #messages.ZcashNetwork.MAINNET,
        "testnet": "Zcash Testnet",  #messages.ZcashNetwork.TESTNET,
    }[network]


@cli.command()
@click.option("-z", "--z-address", help="ZIP-32 Orchard derivation path.")
@click.option(
    "-w", "--network",
    type=click.Choice(["mainnet", "testnet"]),
    default="mainnet",
)
@with_client
def get_fvk(client, z_address, network):
    """Get Zcash Unified Full Incoming Key."""
    return zcash.get_fvk(client, tools.parse_path(z_address), _parse_network(network))

@cli.command()
@click.option("-z", "--z-address", help="ZIP-32 Orchard derivation path.")
@click.option(
    "-w", "--network",
    type=click.Choice(["mainnet", "testnet"]),
    default="mainnet",
)
@with_client
def get_ivk(client, z_address, network):
    """Get Zcash Unified Incoming Viewing Key."""
    return zcash.get_ivk(client, tools.parse_path(z_address), _parse_network(network))

@cli.command(help="""Example:\n
trezorctl zcash get-address -d -t m/44h/133h/0h/0/0 -z m/32h/133h/0h -j 0
""")
@click.option("-t", "--t-address", help="BIP-32 path of a P2PKH transparent address.")
@click.option("-z", "--z-address", help="ZIP-32 Orchard derivation path.")
@click.option("-j", "--diversifier-index", default=0, type=int, help="diversifier index of the shielded address.")
@click.option("-d", "--show-display", is_flag=True)
@click.option(
    "-w", "--network",
    type=click.Choice(["mainnet", "testnet"]),
    default="mainnet",
)
@with_client
def get_address(client, t_address, z_address, diversifier_index, show_display, network):
    """Get Zcash address."""
    if not t_address and not z_address:
        return """Specify address path using -t (transparent) and -z (shielded) arguments.\nYou can use both to get Zcash unified address."""

    kwargs = dict()
    kwargs["show_display"] = show_display
    if t_address:
        kwargs["t_address_n"] = tools.parse_path(t_address)
    if z_address:
        kwargs["z_address_n"] = tools.parse_path(z_address)
        kwargs["diversifier_index"] = diversifier_index

    kwargs["coin_name"] = _parse_network(network)

    try:
        return zcash.get_address(client, **kwargs)
    except ValueError as e:
        return str(e)
