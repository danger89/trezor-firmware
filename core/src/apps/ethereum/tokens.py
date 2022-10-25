# generated from tokens.py.mako
# (by running `make templates` in `core`)
# do not edit manually!
# fmt: off
from trezor.messages import EthereumTokenInfo

UNKNOWN_TOKEN = EthereumTokenInfo(
    symbol="Wei UNKN",
    decimals=0,
    address=b"",
    chain_id=0,
    name="Unknown token",
)


def token_by_chain_address(chain_id: int, address: bytes) -> EthereumTokenInfo | None:
    if chain_id == 1:  # eth
        if address == b"\x7f\xc6\x65\x00\xc8\x4a\x76\xad\x7e\x9c\x93\x43\x7b\xfc\x5a\xc3\x3e\x2d\xda\xe9":
            return EthereumTokenInfo(
                symbol="AAVE",
                decimals=18,
                address=address,
                chain_id=chain_id,
                name="Aave",
            )
        if address == b"\x4d\x22\x44\x52\x80\x1a\xce\xd8\xb2\xf0\xae\xbe\x15\x53\x79\xbb\x5d\x59\x43\x81":
            return EthereumTokenInfo(
                symbol="APE",
                decimals=18,
                address=address,
                chain_id=chain_id,
                name="ApeCoin",
            )
        if address == b"\xbb\x0e\x17\xef\x65\xf8\x2a\xb0\x18\xd8\xed\xd7\x76\xe8\xdd\x94\x03\x27\xb2\x8b":
            return EthereumTokenInfo(
                symbol="AXS",
                decimals=18,
                address=address,
                chain_id=chain_id,
                name="Axie Infinity",
            )
        if address == b"\x4f\xab\xb1\x45\xd6\x46\x52\xa9\x48\xd7\x25\x33\x02\x3f\x6e\x7a\x62\x3c\x7c\x53":
            return EthereumTokenInfo(
                symbol="BUSD",
                decimals=18,
                address=address,
                chain_id=chain_id,
                name="Binance USD",
            )
        if address == b"\x35\x06\x42\x4f\x91\xfd\x33\x08\x44\x66\xf4\x02\xd5\xd9\x7f\x05\xf8\xe3\xb4\xaf":
            return EthereumTokenInfo(
                symbol="CHZ",
                decimals=18,
                address=address,
                chain_id=chain_id,
                name="Chiliz",
            )
        if address == b"\xa0\xb7\x3e\x1f\xf0\xb8\x09\x14\xab\x6f\xe0\x44\x4e\x65\x84\x8c\x4c\x34\x45\x0b":
            return EthereumTokenInfo(
                symbol="CRO",
                decimals=8,
                address=address,
                chain_id=chain_id,
                name="Cronos",
            )
        if address == b"\x6b\x17\x54\x74\xe8\x90\x94\xc4\x4d\xa9\x8b\x95\x4e\xed\xea\xc4\x95\x27\x1d\x0f":
            return EthereumTokenInfo(
                symbol="DAI",
                decimals=18,
                address=address,
                chain_id=chain_id,
                name="Dai",
            )
        if address == b"\x86\xfa\x04\x98\x57\xe0\x20\x9a\xa7\xd9\xe6\x16\xf7\xeb\x3b\x3b\x78\xec\xfd\xb0":
            return EthereumTokenInfo(
                symbol="EOS",
                decimals=18,
                address=address,
                chain_id=chain_id,
                name="EOS",
            )
        if address == b"\x85\x3d\x95\x5a\xce\xf8\x22\xdb\x05\x8e\xb8\x50\x59\x11\xed\x77\xf1\x75\xb9\x9e":
            return EthereumTokenInfo(
                symbol="FRAX",
                decimals=18,
                address=address,
                chain_id=chain_id,
                name="Frax",
            )
        if address == b"\x50\xd1\xc9\x77\x19\x02\x47\x60\x76\xec\xfc\x8b\x2a\x83\xad\x6b\x93\x55\xa4\xc9":
            return EthereumTokenInfo(
                symbol="FTT",
                decimals=18,
                address=address,
                chain_id=chain_id,
                name="FTX",
            )
        if address == b"\x2a\xf5\xd2\xad\x76\x74\x11\x91\xd1\x5d\xfe\x7b\xf6\xac\x92\xd4\xbd\x91\x2c\xa3":
            return EthereumTokenInfo(
                symbol="LEO",
                decimals=18,
                address=address,
                chain_id=chain_id,
                name="LEO Token",
            )
        if address == b"\x51\x49\x10\x77\x1a\xf9\xca\x65\x6a\xf8\x40\xdf\xf8\x3e\x82\x64\xec\xf9\x86\xca":
            return EthereumTokenInfo(
                symbol="LINK",
                decimals=18,
                address=address,
                chain_id=chain_id,
                name="Chainlink",
            )
        if address == b"\x0f\x5d\x2f\xb2\x9f\xb7\xd3\xcf\xee\x44\x4a\x20\x02\x98\xf4\x68\x90\x8c\xc9\x42":
            return EthereumTokenInfo(
                symbol="MANA",
                decimals=18,
                address=address,
                chain_id=chain_id,
                name="Decentraland",
            )
        if address == b"\x7d\x1a\xfa\x7b\x71\x8f\xb8\x93\xdb\x30\xa3\xab\xc0\xcf\xc6\x08\xaa\xcf\xeb\xb0":
            return EthereumTokenInfo(
                symbol="MATIC",
                decimals=18,
                address=address,
                chain_id=chain_id,
                name="Polygon",
            )
        if address == b"\x75\x23\x1f\x58\xb4\x32\x40\xc9\x71\x8d\xd5\x8b\x49\x67\xc5\x11\x43\x42\xa8\x6c":
            return EthereumTokenInfo(
                symbol="OKB",
                decimals=18,
                address=address,
                chain_id=chain_id,
                name="OKB",
            )
        if address == b"\x4a\x22\x0e\x60\x96\xb2\x5e\xad\xb8\x83\x58\xcb\x44\x06\x8a\x32\x48\x25\x46\x75":
            return EthereumTokenInfo(
                symbol="QNT",
                decimals=18,
                address=address,
                chain_id=chain_id,
                name="Quant",
            )
        if address == b"\x38\x45\xba\xda\xde\x8e\x6d\xff\x04\x98\x20\x68\x0d\x1f\x14\xbd\x39\x03\xa5\xd0":
            return EthereumTokenInfo(
                symbol="SAND",
                decimals=18,
                address=address,
                chain_id=chain_id,
                name="The Sandbox",
            )
        if address == b"\x95\xad\x61\xb0\xa1\x50\xd7\x92\x19\xdc\xf6\x4e\x1e\x6c\xc0\x1f\x0b\x64\xc4\xce":
            return EthereumTokenInfo(
                symbol="SHIB",
                decimals=18,
                address=address,
                chain_id=chain_id,
                name="Shiba Inu",
            )
        if address == b"\xae\x7a\xb9\x65\x20\xde\x3a\x18\xe5\xe1\x11\xb5\xea\xab\x09\x53\x12\xd7\xfe\x84":
            return EthereumTokenInfo(
                symbol="STETH",
                decimals=18,
                address=address,
                chain_id=chain_id,
                name="Lido Staked Ether",
            )
        if address == b"\x1f\x98\x40\xa8\x5d\x5a\xf5\xbf\x1d\x17\x62\xf9\x25\xbd\xad\xdc\x42\x01\xf9\x84":
            return EthereumTokenInfo(
                symbol="UNI",
                decimals=18,
                address=address,
                chain_id=chain_id,
                name="Uniswap",
            )
        if address == b"\xa0\xb8\x69\x91\xc6\x21\x8b\x36\xc1\xd1\x9d\x4a\x2e\x9e\xb0\xce\x36\x06\xeb\x48":
            return EthereumTokenInfo(
                symbol="USDC",
                decimals=6,
                address=address,
                chain_id=chain_id,
                name="USD Coin",
            )
        if address == b"\xda\xc1\x7f\x95\x8d\x2e\xe5\x23\xa2\x20\x62\x06\x99\x45\x97\xc1\x3d\x83\x1e\xc7":
            return EthereumTokenInfo(
                symbol="USDT",
                decimals=6,
                address=address,
                chain_id=chain_id,
                name="Tether",
            )
        if address == b"\x22\x60\xfa\xc5\xe5\x54\x2a\x77\x3a\xa4\x4f\xbc\xfe\xdf\x7c\x19\x3b\xc2\xc5\x99":
            return EthereumTokenInfo(
                symbol="WBTC",
                decimals=8,
                address=address,
                chain_id=chain_id,
                name="Wrapped Bitcoin",
            )
        if address == b"\xa2\xcd\x3d\x43\xc7\x75\x97\x8a\x96\xbd\xbf\x12\xd7\x33\xd5\xa1\xed\x94\xfb\x18":
            return EthereumTokenInfo(
                symbol="XCN",
                decimals=18,
                address=address,
                chain_id=chain_id,
                name="Chain",
            )
    if chain_id == 56:  # bnb
        if address == b"\x0e\xb3\xa7\x05\xfc\x54\x72\x50\x37\xcc\x9e\x00\x8b\xde\xde\x69\x7f\x62\xf3\x35":
            return EthereumTokenInfo(
                symbol="ATOM",
                decimals=18,
                address=address,
                chain_id=chain_id,
                name="Cosmos Hub",
            )
    if chain_id == 137:  # MATIC
        if address == b"\x2c\x89\xbb\xc9\x2b\xd8\x6f\x80\x75\xd1\xde\xcc\x58\xc7\xf4\xe0\x10\x7f\x28\x6b":
            return EthereumTokenInfo(
                symbol="AVAX",
                decimals=18,
                address=address,
                chain_id=chain_id,
                name="Avalanche",
            )
    return None
