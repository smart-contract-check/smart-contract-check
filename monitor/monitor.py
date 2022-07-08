import json
from web3 import Web3
import pymongo
import datetime
from threading import Thread, Timer
import logging
import sys
import time
from monitor.known_addresses import KNOWN_ADDRESSES
from dotenv import load_dotenv
import os

load_dotenv()

logger = logging.getLogger(__name__)
handler = logging.FileHandler(f"logs/{__name__}_log.log")
formatter = logging.Formatter('%(asctime)s : %(levelname)s :  %(name)s  : %(funcName)s : %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

db_client = pymongo.MongoClient(os.getenv('MONGODB_INSTANCE'))
scam_db = db_client["eth-scam-checker"]
pairs_collection = scam_db["pairs"]

my_provider = "https://mainnet.infura.io/v3/002262bebeb24a3093c043587f48c428"
router_address = Web3.toChecksumAddress("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D")
factory_address = Web3.toChecksumAddress("0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f")

client = Web3(Web3.HTTPProvider(my_provider))

with open("abi/IUniswapV2Factory.json") as f:
    uniswap_factory = json.load(f)

uniswap_factory_abi = uniswap_factory["abi"]
contract = client.eth.contract(address=factory_address, abi=uniswap_factory_abi)


# with open("abi/ERC20.json") as f:
#     erc20_abi = json.load(f)


class UniswapMonitor(Thread):
    def __init__(self, thread_id, name, queue, wait_time):
        Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.wait_time = wait_time
        self.queue = queue

    def run(self):
        logger.info("Starting " + self.name + " with wait time: " + str(self.wait_time))
        event_filter = contract.events.PairCreated.createFilter(fromBlock='latest')

        while True:
            try:
                for PairCreated in event_filter.get_new_entries():
                    t = Timer(self.wait_time, self.handle_event, args=(PairCreated,))
                    logger.info("Thread waiting to run handle event at: " + str(datetime.datetime.utcnow()))
                    t.start()
                    # self.handle_event(PairCreated)

            except Exception as e:
                logger.critical("Infura PairCreated event failed, recreating eventfilter", exc_info=True)
                try:
                    event_filter = contract.events.PairCreated.createFilter(fromBlock='latest')

                except:
                    logger.warning("Could not recreate eventfilter yet")

            finally:
                time.sleep(30)

    def handle_event(self, event):
        try:
            json_object = json.loads(Web3.toJSON(event))
            token0_address = Web3.toChecksumAddress(json_object['args']['token0'])
            token1_address = Web3.toChecksumAddress(json_object['args']['token1'])

            pair = {
                "pair_address": Web3.toChecksumAddress(json_object['args']['pair']),
                "token0": token0_address,
                "token1": token1_address,
                "blockNumber": json_object['blockNumber'],
                "create_time": time.time()
            }
            pairs_collection.replace_one({"pair_address": Web3.toChecksumAddress(json_object['args']['pair'])}, pair,
                                         upsert=True)

            for token_address in [token0_address, token1_address]:
                if Web3.toChecksumAddress(token_address) not in KNOWN_ADDRESSES:
                    self.queue.put(Web3.toChecksumAddress(token_address))

        except Exception as e:
            logger.error("Exception occurred", exc_info=True)
