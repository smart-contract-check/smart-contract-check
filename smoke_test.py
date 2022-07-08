import time
import sys
import logging
logging.Formatter.converter = time.gmtime
logging.basicConfig(
    handlers=[
        logging.FileHandler("logs/smoke_test.log"),
        logging.StreamHandler(sys.stdout)
    ],
    format='%(asctime)s : %(levelname)s :  %(name)s  : %(funcName)s : %(message)s',
    level=logging.INFO
)

import queue
from controller.api_worker import APIWorker
from test.random_tokens import RANDOM_TOKENS
from dotenv import load_dotenv

load_dotenv(".env")


def smoke_test(api_queue):
    for address in RANDOM_TOKENS:
        api_queue.put(address)


def test_specific_token(api_queue, token):
    api_queue.put(token)


def main():
    api_queue = queue.Queue()

    api_worker = APIWorker("API Worker", api_queue, "smoke-test-eth-scam-checker")
    api_worker.start()

    smoke_test(api_queue)


if __name__ == '__main__':
    main()
