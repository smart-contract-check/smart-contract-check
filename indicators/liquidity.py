import pymongo
from web3 import Web3
import json
from decimal import Decimal
import logging
import sys
import time
from exceptions.exceptions import *
from dotenv import load_dotenv
import os

load_dotenv()

logger = logging.getLogger(__name__)
handler = logging.FileHandler(f"logs/{__name__}_log.log")
formatter = logging.Formatter('%(asctime)s : %(levelname)s :  %(name)s  : %(funcName)s : %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

my_provider = os.getenv('INFURA_PROVIDER')

with open("abi/UniswapV2Factory.json") as f:
    UniswapV2Factory_abi = json.load(f)

with open("abi/ERC20.json") as f:
    erc20_abi = json.load(f)

with open("abi/UniswapPair.json") as f:
    pair_abi = json.load(f)

client = Web3(Web3.HTTPProvider(my_provider))

UniswapV2Factory = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
WETH_ADDR = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
WETH_DECIMALS = 18

SNAP_ADDR = "0xe2fe530c047f2d85298b07d9333c05737f1435fb"


def get_liquidity(token):
    try:
        contract_factory = client.eth.contract(address=UniswapV2Factory, abi=UniswapV2Factory_abi)
        pair = contract_factory.functions.getPair(token, WETH_ADDR).call()

    except Exception as e:
        logger.error("Exception occurred", exc_info=True)
        raise APIError(e)

    if pair == '0x0000000000000000000000000000000000000000':
        logger.warning(f"There exists no WETH pair for token {token}")
        return {
            "address": token,
            "eth_liquidity": None,
            "lp_address": pair,
            "error": "There exists no WETH pair with requested token"
        }

    try:
        contract_pair = client.eth.contract(address=pair, abi=pair_abi)
        [reserves0, reserves1, block_timestamp] = contract_pair.functions.getReserves().call()
        decimals = contract_pair.functions.decimals().call()

    except Exception as e:
        logger.error("Exception occurred", exc_info=True)
        raise APIError(e)

    if int(token, 16) > int(WETH_ADDR, 16):
        token_eth_liquidity = Decimal(reserves0) / Decimal(10 ** decimals)
        token0 = WETH_ADDR
        token1 = token
    else:
        token_eth_liquidity = Decimal(reserves1) / Decimal(10 ** decimals)
        token0 = token
        token1 = WETH_ADDR

    logger.info(token_eth_liquidity)

    liquidity_information = {
        "address": token,
        "eth_liquidity": str(token_eth_liquidity),
        "lp_address": pair,
        "token0": token0,
        "token1": token1,
        "reserves0": str(reserves0),
        "reserves1": str(reserves1),
        "decimals": decimals
    }

    return liquidity_information
    # https://api.ethplorer.io/getTopTokenHolders/0x0f14F11f16C267939CE3DFA6cFDfc81E4aa8D08F?apiKey=freekey



