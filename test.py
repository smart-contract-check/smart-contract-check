import time
import sys
import logging
logging.Formatter.converter = time.gmtime
logging.basicConfig(
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/test_full_log.log"),
    ],
    format='%(asctime)s : %(levelname)s :  %(name)s  : %(funcName)s : %(message)s',
    level=logging.INFO
)
import pymongo
import datetime
import queue
from web3 import Web3
from controller.api_worker import APIWorker
import indicators.verified_contract
from indicators import *


def test_specific_token(api_queue, token):
    api_queue.put(token)


def main():
    # verification_test()
    api_queue = queue.Queue()

    api_worker = APIWorker("API Worker", api_queue, "test-eth-scam-checker")
    api_worker.start()

    # update_all(api_queue)
    # test_specific_token(api_queue, Web3.toChecksumAddress('0x866889fDBA07D4F044419e6a99710938F2268690'))  # working token
    # test_specific_token(api_queue, Web3.toChecksumAddress('0x03ae79862b5657c19cfc750fce6b0bb5a0fd9a29'))  # scam token
    test_specific_token(api_queue, Web3.toChecksumAddress('0x4470BB87d77b963A013DB939BE332f927f2b992e'))  # slither error token
    # test_specific_token(api_queue, Web3.toChecksumAddress('0x34F3C739FDa443997B5b2CAC9cb42e448B28d45D'))  # doesnt compile token
    # test_specific_token(api_queue, Web3.toChecksumAddress('0x3F4B23B8EA03598d25F1bc7d32AA45B832dBBa16'))  # wierd sourcecode token
    # test_specific_token(api_queue, Web3.toChecksumAddress('0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2'))


if __name__ == '__main__':
    main()
