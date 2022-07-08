import requests
import logging
from exceptions.exceptions import *

logger = logging.getLogger(__name__)
handler = logging.FileHandler(f"logs/{__name__}_log.log")
formatter = logging.Formatter('%(asctime)s : %(levelname)s :  %(name)s  : %(funcName)s : %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

HONEYPOT_IS_URL = 'https://aywt3wreda.execute-api.eu-west-1.amazonaws.com/default/IsHoneypot?chain=eth&token='


def honeypot_is(token):
    try:
        response = requests.get(HONEYPOT_IS_URL + token)
    except Exception as e:
        logger.error("Exception occurred", exc_info=True)
        raise APIError(e)

    if response.status_code != 200:
        error = APIError(f"honeypot_is for token at {token} failed with error {response.text}")
        logger.error(error)
        raise error

    honeypot_info = response.json()

    logger.info(honeypot_info)
    honeypot_result = {
        'address': token,
        'IsHoneypot': honeypot_info['IsHoneypot'],
        'Error': str(honeypot_info['Error']),
        'MaxTxAmount': str(honeypot_info['MaxTxAmount']),
        'MaxTxAmountETH': str(honeypot_info['MaxTxAmountBNB']),
        'BuyTax': str(honeypot_info['BuyTax']),
        'SellTax': str(honeypot_info['SellTax']),
        'BuyGas': str(honeypot_info['BuyGas']),
        'SellGas': str(honeypot_info['SellGas']),
    }

    return honeypot_result
