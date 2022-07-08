import json
from etherscan import Etherscan
import logging
import sys
import time
from exceptions.exceptions import *
import indicators.slither
import slither.exceptions
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
handler = logging.FileHandler(f"logs/{__name__}_log.log")
formatter = logging.Formatter('%(asctime)s : %(levelname)s :  %(name)s  : %(funcName)s : %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

eth = Etherscan(os.getenv('ETHERSCAN_API_KEY'))


def process_verified_contract(token):

    try:

        [result] = eth.get_contract_source_code(address=token)

    except Exception as e:
        logger.error("Exception occurred", exc_info=True)
        raise APIError(e)

    result['address'] = token
    is_not_verified = result['SourceCode'] == ""

    slither_results = process_slither(token, is_not_verified)

    result['slither_results'] = slither_results

    return result


def process_slither(token, is_not_verified):
    slither_result = {
            "address": token,
            "error": 2,  # contract not verified
            "vulnerabilities": []
    }

    if is_not_verified:
        return slither_result

    # try:
    #     multiple_sourcecodes = ""
    #     source_code_obj = json.loads(source_code[1:-1])
    #     source_code = ""
    #     for s in source_code_obj['sources']:
    #         source_code += source_code_obj['sources'][s]['content'] + "\n"
    #     print(multiple_sourcecodes)
    #
    # except Exception as e:
    #     pass
    #

    # filename = f"data/{token}.sol"
    # file = open(filename, "w")
    # file.write(source_code)
    # file.close()

    try:
        vulnerabilities = indicators.slither.get_slither_results(token)

    except slither.exceptions.SlitherError as e:
        logger.error("SlitherError occurred", exc_info=True)
        return {
            "address": token,
            "error": 1,
            "vulnerabilities": []
        }

    except Exception as e:
        logger.error("Unknown Error", exc_info=True)
        return {
            "address": token,
            "error": 1,  # exception
            "vulnerabilities": []
        }

    slither_result['error'] = 0
    slither_result['vulnerabilities'] = vulnerabilities

    return slither_result


