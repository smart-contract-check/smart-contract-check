from web3 import Web3
import json
import logging
from exceptions.exceptions import *
import requests
from dotenv import load_dotenv
import os

load_dotenv()


logger = logging.getLogger(__name__)
handler = logging.FileHandler(f"logs/{__name__}_log.log")
formatter = logging.Formatter('%(asctime)s : %(levelname)s :  %(name)s  : %(funcName)s : %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

my_provider = os.getenv('INFURA_PROVIDER')

ETHPLORER_API_KEY = f"?apiKey={os.getenv('ETHPLORER_API_KEY')}"
ETHPLORER_URL = 'https://api.ethplorer.io/'

TOP_TOKEN_HOLDERS = 'getTopTokenHolders/'
#{"holders":[{"address":"0x0f14f11f16c267939ce3dfa6cfdfc81e4aa8d08f","balance":7.34069560690117e+20,"share":73.41},{"address":"0x7e32fc6d50b4be6218004e10991f2e4b85d335e2","balance":5.3419723025813225e+19,"share":5.34},{"address":"0x995bfbcb635827556b1c4bb060cb7562a9b11b6d","balance":1.8345561865840257e+19,"share":1.83},{"address":"0x89e03f21434858f4709d5ada9e077a33a9992603","balance":1.3303353353332476e+19,"share":1.33},{"address":"0xa5e499c77522c6e7a2867b68ef52f5e5dac3dbde","balance":9.632064599714652e+18,"share":0.96},{"address":"0xd188427ebd42d7a0ffee6f5369c5e1c3b9fab94e","balance":9.371894228771858e+18,"share":0.94},{"address":"0x2acdd73ee771a427ebfc7c481753b4f4bdd44a9e","balance":8.669029065938794e+18,"share":0.87},{"address":"0x650509e1b481975637801b091b4adc19e1f4ff4d","balance":8.622849640390919e+18,"share":0.86},{"address":"0x46703442485a2dd68461ea648ffda85f335d7fda","balance":8.619840499872776e+18,"share":0.86},{"address":"0xfaa289083ac098cd2274d64ed98b1b678657c4f1","balance":8.409929333739744e+18,"share":0.84}]}

TOKEN_INFO = 'getTokenInfo/' # &limit=100


with open("abi/UniswapPair.json") as f:
    pair_abi = json.load(f)
with open("abi/UniswapV2Factory.json") as f:
    UniswapV2Factory_abi = json.load(f)

UniswapV2Factory = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"

client = Web3(Web3.HTTPProvider(my_provider))

WETH_ADDR = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
WETH_DECIMALS = 18


# https://api.ethplorer.io/getTopTokenHolders/0x0f14F11f16C267939CE3DFA6cFDfc81E4aa8D08F?apiKey=freekey
def get_liquidity_holders(token):

    try:
        contract_factory = client.eth.contract(address=UniswapV2Factory, abi=UniswapV2Factory_abi)
        pair = contract_factory.functions.getPair(token, WETH_ADDR).call()
    except Exception as e:
        logger.error("Exception occurred", exc_info=True)
        raise APIError(e)

    logger.info(f"liquidity pair with WETH at : {pair}")

    if pair == '0x0000000000000000000000000000000000000000':
        logger.warning(f"There exists no WETH pair for token {token}")
        return {
            "address": token,
            "pair": pair,
            "holdersCount": None,
            "holders": None,
            "error": "There exists no WETH pair with requested token"
        }

    try:
        lp_info = requests.get(ETHPLORER_URL + TOKEN_INFO + pair + ETHPLORER_API_KEY)
        locked_liquidity_holders = requests.get(ETHPLORER_URL + TOP_TOKEN_HOLDERS + pair + ETHPLORER_API_KEY)
    except Exception as e:
        logger.error("Exception occurred", exc_info=True)
        raise APIError(e)

    if lp_info.status_code != 200:
        raise APIError(f"getTokenInfo for pair at {pair} failed with error {lp_info.text}")

    if locked_liquidity_holders.status_code != 200:
        raise APIError(f"getTopTokenHolders for pair at {pair} failed with error {locked_liquidity_holders.text}")

    lp_info = lp_info.json()
    locked_liquidity_holders = locked_liquidity_holders.json()

    # logger.info(locked_liquidity_holders)

    for holder in locked_liquidity_holders['holders']:
        holder['address'] = Web3.toChecksumAddress(holder['address'])

    locked_liquidity_info = {
        "address": token,
        "pair": pair,
        "holdersCount": lp_info['holdersCount'],
        "holders": locked_liquidity_holders['holders']
    }

    logger.info(locked_liquidity_info)
    return locked_liquidity_info
