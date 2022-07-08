import time
import sys
import logging
logging.Formatter.converter = time.gmtime
logging.basicConfig(
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/main_full_log.log"),
    ],
    format='%(asctime)s : %(levelname)s :  %(name)s  : %(funcName)s : %(message)s',
    level=logging.INFO
)
import queue
from controller.api_worker import APIWorker
from monitor.monitor import UniswapMonitor
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()



def main():
    # make queue here and give it to monitor
    main_queue = queue.Queue()

    api_worker = APIWorker("API Worker", main_queue, "eth-scam-checker")
    api_worker.start()

    monitor_thread = UniswapMonitor(1, "Uniswap Monitor", main_queue, 300.0)

    monitor_thread.start()
    time.sleep(2)

    # monitor_thread.join()


if __name__ == '__main__':
    main()

