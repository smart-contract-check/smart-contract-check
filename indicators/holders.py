import requests
import logging
from requests import Response
from web3 import Web3
from exceptions.exceptions import *
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
handler = logging.FileHandler(f"logs/{__name__}_log.log")
formatter = logging.Formatter('%(asctime)s : %(levelname)s :  %(name)s  : %(funcName)s : %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


ETHPLORER_API_KEY = f"?apiKey={os.getenv('ETHPLORER_API_KEY')}"
ETHPLORER_URL = 'https://api.ethplorer.io/'

TOKEN_INFO = 'getTokenInfo/' # &limit=100
# {"address":"0xc554c7543b6b837daf547b3a832ebe0e39ecb9dd","decimals":"9","name":"TakashINU Murakami","owner":"0x0000000000000000000000000000000000000000","symbol":"TakashINU","totalSupply":"1000000000000000000000","transfersCount":500,"lastUpdated":1650494560,"issuancesCount":0,"holdersCount":158,"ethTransfersCount":0,"price":false,"countOps":500}

TOP_TOKEN_HOLDERS = 'getTopTokenHolders/'
#{"holders":[{"address":"0x0f14f11f16c267939ce3dfa6cfdfc81e4aa8d08f","balance":7.34069560690117e+20,"share":73.41},{"address":"0x7e32fc6d50b4be6218004e10991f2e4b85d335e2","balance":5.3419723025813225e+19,"share":5.34},{"address":"0x995bfbcb635827556b1c4bb060cb7562a9b11b6d","balance":1.8345561865840257e+19,"share":1.83},{"address":"0x89e03f21434858f4709d5ada9e077a33a9992603","balance":1.3303353353332476e+19,"share":1.33},{"address":"0xa5e499c77522c6e7a2867b68ef52f5e5dac3dbde","balance":9.632064599714652e+18,"share":0.96},{"address":"0xd188427ebd42d7a0ffee6f5369c5e1c3b9fab94e","balance":9.371894228771858e+18,"share":0.94},{"address":"0x2acdd73ee771a427ebfc7c481753b4f4bdd44a9e","balance":8.669029065938794e+18,"share":0.87},{"address":"0x650509e1b481975637801b091b4adc19e1f4ff4d","balance":8.622849640390919e+18,"share":0.86},{"address":"0x46703442485a2dd68461ea648ffda85f335d7fda","balance":8.619840499872776e+18,"share":0.86},{"address":"0xfaa289083ac098cd2274d64ed98b1b678657c4f1","balance":8.409929333739744e+18,"share":0.84}]}

ADDRESS_INFO = 'getAddressInfo/'
# {"address":"0x4504bfbf4ae479f179453db2f5b65abb9ccd5502","ETH":{"price":{"rate":2823.268719613443,"diff":-4.99,"diff7d":-4.72,"ts":1651257120,"marketCapUsd":340426507977.39307,"availableSupply":120578854.4365,"volume24h":16900787203.234087,"diff30d":-16.79976047091172,"volDiff1":-7.135059386731442,"volDiff7":12.902544283250194,"volDiff30":18.984336465798066},"balance":0,"rawBalance":"0"},"countTxs":69,"contractInfo":{"creatorAddress":null,"transactionHash":"0x16832c8b57c429a688a338666386b77ff18112507269167f87ccfddebb43d9ec","timestamp":1645941258},"tokenInfo":{"address":"0x4504bfbf4ae479f179453db2f5b65abb9ccd5502","decimals":"18","name":"Ukraine DAO","symbol":"Ukraine","totalSupply":"1000000000000000000000000000000","lastUpdated":1646051509,"issuancesCount":0,"holdersCount":175,"ethTransfersCount":0,"price":false}}


def get_holders(token):

    try:
        token_info = requests.get(ETHPLORER_URL + TOKEN_INFO + token + ETHPLORER_API_KEY)
        token_top_holders: Response = requests.get(ETHPLORER_URL + TOP_TOKEN_HOLDERS + token + ETHPLORER_API_KEY)
    except Exception as e:
        logger.error("Exception occurred", exc_info=True)
        raise APIError(e)

    if token_info.status_code != 200:
        error = APIError(f"getTokenInfo for token at {token} with error {token_info.text}")
        logger.error(error)
        raise error

    if token_top_holders.status_code != 200:
        error = APIError(f"getTokenInfo for token at {token} failed with error {token_top_holders.text}")
        logger.error(error)
        raise error

    token_info = token_info.json()
    token_top_holders = token_top_holders.json()

    logger.info(token_top_holders)

    for holder in token_top_holders['holders']:
        holder['address'] = Web3.toChecksumAddress(holder['address'])

    holders_info = {
        "address": token,
        "holdersCount": token_info['holdersCount'],
        "holders": token_top_holders['holders']
    }
    return holders_info



