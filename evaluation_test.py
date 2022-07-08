import time
import sys
import logging
logging.Formatter.converter = time.gmtime
logging.basicConfig(
    handlers=[
        logging.FileHandler("logs/evaluation_test_log.log"),
        logging.StreamHandler(sys.stdout)
    ],
    format='%(asctime)s : %(levelname)s :  %(name)s  : %(funcName)s : %(message)s',
    level=logging.INFO
)
import pymongo
import datetime
import queue
from web3 import Web3
from evaluation.evaluator import Evaluator
import evaluation.evaluation_config
from controller.api_worker import APIWorker
import indicators.verified_contract
from indicators import *
from dotenv import load_dotenv
import os

load_dotenv()


db_client = pymongo.MongoClient("mongodb://localhost:27017/")
scam_db = db_client["eth-scam-checker"]
manual_scam_db = db_client["manual-eth-scam-checker"]

scanned_tokens_collection = scam_db["scanned_tokens"]


def evaluate_monitor():

    # config = {
    #     "score_liquidity_share": evaluation.evaluation_config.score_liquidity_share,
    #     "score_holder_share": evaluation.evaluation_config.score_holder_share,
    #     "score_liquidity_amount": evaluation.evaluation_config.score_liquidity_amount,
    #     "score_vulnerabilities": evaluation.evaluation_config.score_vulnerabilities
    # }

    test_results = scanned_tokens_collection.find()
    for token in test_results:
        evaluator = Evaluator(token, evaluation.evaluation_config.DEFAULT_CONFIG)
        result = evaluator.get_score()
        print(token['address'])
        print(result)


def evaluate_specific_submission(token_address):

    # config = {
    #     "score_liquidity_share": evaluation.evaluation_config.score_liquidity_share,
    #     "score_holder_share": evaluation.evaluation_config.score_holder_share,
    #     "score_liquidity_amount": evaluation.evaluation_config.score_liquidity_amount,
    #     "score_vulnerabilities": evaluation.evaluation_config.score_vulnerabilities
    # }

    token = manual_scam_db.scanned_tokens.find_one({"address": Web3.toChecksumAddress(token_address)})
    evaluator = Evaluator(token, evaluation.evaluation_config.DEFAULT_CONFIG)
    result = evaluator.get_score()
    print(token['address'])
    print(result)


if __name__ == '__main__':
    evaluate_monitor()
    # evaluate_specific_submission("0x1BF0c586176Fd47b2e6285E4293F8B65bcc8Ebff")

