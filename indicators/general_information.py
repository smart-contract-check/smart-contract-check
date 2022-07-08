from web3 import Web3
import json
from decimal import Decimal
import logging
import requests
from etherscan import Etherscan
from requests import Response
from exceptions.exceptions import *
from dotenv import load_dotenv
import os

load_dotenv()

logger = logging.getLogger(__name__)
handler = logging.FileHandler(f"logs/{__name__}_log.log")
formatter = logging.Formatter('%(asctime)s : %(levelname)s :  %(name)s  : %(funcName)s : %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

eth = Etherscan(os.getenv("ETHERSCAN_API_KEY"))
my_provider = os.getenv("INFURA_PROVIDER")

with open("abi/ERC20.json") as f:
    erc20_abi = json.load(f)

with open("abi/UniswapV2Factory.json") as f:
    UniswapV2Factory_abi = json.load(f)

client = Web3(Web3.HTTPProvider(my_provider))

UniswapV2Factory = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
WETH_ADDR = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"


ETHPLORER_API_KEY = f"?apiKey={os.getenv('ETHPLORER_API_KEY')}"
ETHPLORER_URL = 'https://api.ethplorer.io/'

TOKEN_INFO = 'getTokenInfo/'


def general_information(token):

    contract_factory = client.eth.contract(address=UniswapV2Factory, abi=UniswapV2Factory_abi)
    pair = contract_factory.functions.getPair(token, WETH_ADDR).call()

    contract_token = client.eth.contract(address=token, abi=erc20_abi)
    token_symbol = contract_token.functions.symbol().call()  # can sometimes throw, i guess we let the exception bubble up
    token_name = contract_token.functions.name().call()
    token_supply = contract_token.functions.totalSupply().call()
    decimals = contract_token.functions.decimals().call()
    token_human_supply = Decimal(token_supply) / Decimal(10 ** decimals)

    try:
        tx_info = eth.get_normal_txs_by_address(address=token, startblock=0, endblock=99999999, sort="asc")

        creator = tx_info[0]['from']
        creation_time = tx_info[0]['timeStamp']
        creation_block = tx_info[0]['blockNumber']
        creation_tx_hash = tx_info[0]['hash']

        token_info = requests.get(ETHPLORER_URL + TOKEN_INFO + token + ETHPLORER_API_KEY)
        if token_info.status_code != 200:
            error = APIError(f"getTokenInfo for token at {token} with error {token_info.text}")
            logger.error(error)
            raise error

        token_info = token_info.json()
        owner = token_info['owner']
        transfers_count = token_info['transfersCount']

    except Exception as e:
        logger.error("Exception occurred", exc_info=True)
        raise APIError(e)

    token_general_info = {
        "address": token,
        "symbol": token_symbol,
        "name": token_name,
        "weth_pair": pair,
        "supply": str(token_supply),
        "human_supply": str(token_human_supply),
        "decimals": decimals,
        "creator": creator,
        "creation_time": int(creation_time),
        "creation_block": int(creation_block),
        "creation_tx_hash": creation_tx_hash,
        "owner": owner,
        "transfers_count": transfers_count
    }

    return token_general_info



