# generated from tokens.py.mako
# (by running `make templates` in `core`)
# do not edit manually!
# fmt: off
from trezor.messages import EthereumTokenInfo
<%
from collections import defaultdict

def group_tokens(tokens):
    r = defaultdict(list)
    for t in sorted(tokens, key=lambda t: t.chain_id):
        r[t.chain_id].append(t)
    return r
%>\

UNKNOWN_TOKEN = EthereumTokenInfo(
    symbol="Wei UNKN",
    decimals=0,
    address=b"",
    chain_id=0,
    name="Unknown token",
)


def token_by_chain_address(chain_id: int, address: bytes) -> EthereumTokenInfo | None:
% for token_chain_id, tokens in group_tokens(supported_on("trezor2", erc20)).items():
    if chain_id == ${token_chain_id}:  # ${tokens[0].chain}
        % for t in tokens:
        if address == ${black_repr(t.address_bytes)}:
            return EthereumTokenInfo(
                symbol=${black_repr(t.symbol)},
                decimals=${t.decimals},
                address=address,
                chain_id=chain_id,
                name=${black_repr(t.name.strip())},
            )
        % endfor
% endfor
    return None
