# generated from networks.py.mako
# (by running `make templates` in `core`)
# do not edit manually!
from typing import Iterator

from trezor.messages import EthereumNetworkInfo

from apps.common.paths import HARDENED

UNKNOWN_NETWORK = EthereumNetworkInfo(
    chain_id=0,
    slip44=0,
    shortcut="UNKN",
    name="Unknown network",
)


def by_chain_id(chain_id: int) -> EthereumNetworkInfo | None:
    for n in _networks_iterator():
        if n.chain_id == chain_id:
            return n
    return None


def by_slip44(slip44: int) -> EthereumNetworkInfo | None:
    for n in _networks_iterator():
        if n.slip44 == slip44:
            return n
    return None


def all_slip44_ids_hardened() -> Iterator[int]:
    for n in _networks_iterator():
        yield n.slip44 | HARDENED


# fmt: off
def _networks_iterator() -> Iterator[EthereumNetworkInfo]:
    yield EthereumNetworkInfo(
        chain_id=1,
        slip44=60,
        shortcut="ETH",
        name="Ethereum",
    )
    yield EthereumNetworkInfo(
        chain_id=3,
        slip44=1,
        shortcut="tROP",
        name="Ropsten",
    )
    yield EthereumNetworkInfo(
        chain_id=4,
        slip44=1,
        shortcut="tRIN",
        name="Rinkeby",
    )
    yield EthereumNetworkInfo(
        chain_id=5,
        slip44=1,
        shortcut="tGOR",
        name="Görli",
    )
    yield EthereumNetworkInfo(
        chain_id=56,
        slip44=714,
        shortcut="BNB",
        name="Binance Smart Chain",
    )
    yield EthereumNetworkInfo(
        chain_id=61,
        slip44=61,
        shortcut="ETC",
        name="Ethereum Classic",
    )
    yield EthereumNetworkInfo(
        chain_id=137,
        slip44=966,
        shortcut="MATIC",
        name="Polygon",
    )
