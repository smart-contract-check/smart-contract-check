import time
import sys
import logging
logging.Formatter.converter = time.gmtime
logging.basicConfig(
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/migration.log"),
    ],
    format='%(asctime)s : %(levelname)s :  %(name)s  : %(funcName)s : %(message)s',
    level=logging.INFO
)
import indicators.verified_contract
import indicators.slither
from exceptions.exceptions import *
import slither.exceptions
import pymongo
import queue
import requests
from web3 import Web3
from controller.api_worker import APIWorker
from test.random_tokens import RANDOM_TOKENS
import evaluation.evaluation_config
from evaluation.evaluator import Evaluator
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

db_client = pymongo.MongoClient(os.getenv('MONGODB_INSTANCE'))
scam_db = db_client["eth-scam-checker"]
scanned_tokens_collection = scam_db["scanned_tokens"]

ETHPLORER_API_KEY = f"?apiKey={os.getenv('ETHPLORER_API_KEY')}"
ETHPLORER_URL = 'https://api.ethplorer.io/'

TOKEN_INFO = 'getTokenInfo/'  # &limit=100


def update_liquidity_amount():
    scanned_tokens = scanned_tokens_collection.find({"liquidity_amount.error": {"$exists": True}})
    for scanned_token in scanned_tokens:
        address = scanned_token['address']
        scanned_tokens_collection.update_one({"address": address},
                                             {"$set": {"liquidity_amount.eth_liquidity": None}})
        # time.sleep(2)

def query_list_of_contracts():
    pass


def update_liquidity_holder_error():
    scanned_tokens = scanned_tokens_collection.find({"liquidity_holders.error": {"$exists": True}})
    for scanned_token in scanned_tokens:
        address = scanned_token['address']
        scanned_tokens_collection.update_one({"address": address},
                                             {"$set": {"liquidity_holders.holdersCount": None}})
        scanned_tokens_collection.update_one({"address": address},
                                             {"$set": {"liquidity_holders.holders": None}})

        # time.sleep(2)


def update_evaluator_results():

    scanned_tokens = scanned_tokens_collection.find()
    for scanned_token in scanned_tokens:
        address = scanned_token['address']

        evaluator = Evaluator(scanned_token, evaluation.evaluation_config.DEFAULT_CONFIG)
        indicator_results = evaluator.get_score()
        scanned_tokens_collection.update_one({"address": address},
                                             {"$set": {"indicator_results": indicator_results}})
        logger.info(address)
        logger.info(indicator_results)


def update_slither_results():

    for token in scam_db.scanned_tokens.find():
        if token['verified_contract']['slither_results']['error'] == 1 and token['verified_contract']['SourceCode'] != "":
            token_address = token['address']
            slither_result = {
                "address": token_address,
                "error": 1,
                "vulnerabilities": []
            }

            try:
                vulnerabilities = indicators.slither.get_slither_results(token_address)

            except slither.exceptions.SlitherError as e:
                logger.error("SlitherError occurred", exc_info=True)
                return slither_result

            except Exception as e:
                logger.error("Unknown Error", exc_info=True)
                return slither_result

            slither_result['error'] = 0
            slither_result['vulnerabilities'] = vulnerabilities
            logger.info(scam_db.scanned_tokens.find_one({"address": token_address}, {"verified_contract.slither_results": 1}))
            logger.info(slither_result)
            logger.info("updated")
            scam_db.scanned_tokens.update_one({"address": token_address}, {"$set": {"verified_contract.slither_results": slither_result}})
            time.sleep(5)


def get_token_info(token, attempts, max_attempts):
    if attempts == max_attempts:
        raise APIError(f"max_attempts {max_attempts} used up")
    attempts += 1
    resp = requests.get(ETHPLORER_URL + TOKEN_INFO + token + ETHPLORER_API_KEY)
    if resp.status_code != 200:
        logger.warning(f"request failed with errorcode {resp.status_code}, retrying attempt {attempts}")
        time.sleep(5)
        get_token_info(token, attempts, max_attempts)

    return resp.json()


def update_owner():
    scanned_tokens = scanned_tokens_collection.find()
    for scanned_token in scanned_tokens:
        address = scanned_token['address']
        try:
            token_info = get_token_info(address, 0, 5)
        except APIError as e:
            logger.error(f"Token {address} failed to get tokenInfo")
        except Exception as tf:
            logger.critical(f"Token {address} failed to get tokenInfo, unexpected error", exc_info=True)

        scanned_tokens_collection.update_one({"address": address},
                                             {"$set": {"owner": str(token_info['owner'])}})
        scanned_tokens_collection.update_one({"address": address},
                                             {"$set": {"transfers_count": token_info['transfersCount']}})
        time.sleep(2)
        print(str(token_info['owner']))


def update_14_05_22():

    api_queue = queue.Queue()

    # for old_token in old_scanned_tokens_collection.find():
    #     old_pair = old_pairs_collection.find_one({
    #         "$or": [
    #             {"token0": old_token['honeypot']['address']},
    #             {"token1": old_token['honeypot']['address']}
    #         ]
    #     })
    #     scan_time = old_pair['create_time']
    #     print(scan_time)
    for old_token in scam_db.scanned_tokens.find({"scan_time": {"$exists": True}}):
        new_verified_contract = old_token['verified_contract']
        try:
            new_verified_contract = indicators.verified_contract.process_verified_contract(old_token['general_information']['address'])

            general_information = old_token['general_information']
            general_information['honeypot'] = old_token['honeypot']
            general_information['holders'] = old_token['holders']
            general_information['liquidity_amount'] = old_token['liquidity_amount']
            general_information['liquidity_holders'] = old_token['liquidity_holders']
            general_information['verified_contract'] = new_verified_contract
            general_information['scan_time'] = old_token['scan_time']
            scam_db.scanned_tokens.replace_one({"address": old_token['general_information']['address']},
                                                        general_information, upsert=True)

        except APIError as a:
            logger.error("An Indicator failed, sending to retry", exc_info=True)
            print(old_token['general_information']['address'])
        finally:
            time.sleep(30)


if __name__ == '__main__':
    print("hello wrld")
    # update_evaluator_results()
    # update_liquidity_holder_error()
    # update_liquidity_amount()
