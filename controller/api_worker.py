import datetime
from threading import Thread, Timer
import pymongo.errors
from evaluation import binary_evaluator
from evaluation import extendet_evaluator
from evaluation.evaluator import Evaluator
import evaluation.evaluation_config
from exceptions.exceptions import *
from collector import token_collector
from evaluation.evaluator import Evaluator
import logging
import time
from dotenv import load_dotenv
import os

load_dotenv()



logger = logging.getLogger(__name__)
handler = logging.FileHandler(f"logs/{__name__}_log.log")
formatter = logging.Formatter('%(asctime)s : %(levelname)s :  %(name)s  : %(funcName)s : %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


db_client = pymongo.MongoClient(os.getenv('MONGODB_INSTANCE'))
scan_history_db = db_client['scan-history']

class APIWorker(Thread):
    """Thread executing tasks from a given tasks queue"""

    def __init__(self, name, queue, scam_db):
        Thread.__init__(self)
        self.name = name
        self.queue = queue
        self.scam_db = db_client[scam_db]
        self.failed_token_collection = self.scam_db["failed_tokens"]
        self.dropped_token_collection = self.scam_db["dropped_tokens"]
        self.scanned_tokens_collection = self.scam_db["scanned_tokens"]
        # self.daemon = True

    def handle_retries(self, token, reason):
        failed_token = {
            "address": token,
            "reason": reason,
        }
        self.failed_token_collection.insert_one(failed_token)
        query = {"address": token}
        retry_count = self.failed_token_collection.count_documents(query)
        if retry_count < 6:
            wait_time = 60 * (2 ** retry_count)
            t = Timer(wait_time, lambda x: self.queue.put(x), args=(token,))
            logger.info(f"Failed token : {token} will retry in {wait_time} seconds from {str(datetime.datetime.utcnow())}")
            t.start()
        else:
            self.dropped_token_collection.insert_one(failed_token)
            logger.error(f"Dropping retries for token: {token}")

    def run(self):
        logger.info("Starting " + self.name)

        # keep running
        while True:
            # get a task

            token = self.queue.get()  # blocking until result is available
            logger.info("Processing: " + token)

            try:

                scanned_token_entry = token_collector.collect_token_details(token)

                # config = {
                #     "score_liquidity_share": evaluation.evaluation_config.score_liquidity_share,
                #     "score_holder_share": evaluation.evaluation_config.score_holder_share,
                #     "score_liquidity_amount": evaluation.evaluation_config.score_liquidity_amount,
                #     "score_vulnerabilities": evaluation.evaluation_config.score_vulnerabilities
                # }

                evaluator = Evaluator(scanned_token_entry, evaluation.evaluation_config.DEFAULT_CONFIG)

                indicator_results, final_score = evaluator.get_score()

                scanned_token_entry["indicator_results"] = indicator_results
                scanned_token_entry["combined_score"] = final_score

                custom_scam_result, custom_scam_probability = evaluator.get_custom_scam_result()

                scanned_token_entry["custom_scam_result"] = int(custom_scam_result[0])
                scanned_token_entry["custom_scam_probability"] = float(custom_scam_probability[0][1])

                svm_scam_result, svm_scam_probability = evaluator.get_svm_scam_result()

                scanned_token_entry["svm_scam_result"] = int(svm_scam_result[0])
                scanned_token_entry["svm_scam_probability"] = float(svm_scam_probability[0][1])

                xgb_scam_result, xgb_scam_probability = evaluator.get_xgb_scam_result()

                scanned_token_entry["xgboost_scam_result"] = int(xgb_scam_result[0])
                scanned_token_entry["xgboost_scam_probability"] = float(xgb_scam_probability[0])

                logger.info(indicator_results)
                logger.info(f"Results: \n"
                            f"Custom probability: {float(custom_scam_probability[0][1])} \n"
                            f"SVM probability: {float(svm_scam_probability[0][1])} \n"
                            f"XGBoost probability: {float(xgb_scam_probability[0])}")

                self.scanned_tokens_collection.replace_one({"address": token}, scanned_token_entry, upsert=True)
                scan_history_db.scanned_tokens.insert_one(scanned_token_entry)

                logger.info(f"Inserting {token} into {self.scam_db.name}.{self.scanned_tokens_collection.name}")
            except APIError as a:
                logger.warning("An Indicator failed, sending to retry", exc_info=True)
                self.handle_retries(token, repr(a))

            except Exception as e:
                # so we move on and handle it in whatever way the caller wanted
                logger.error(f"Unrecoverable exception occured at token {token}", exc_info=True)

            finally:
                # task complete no matter what happened
                time.sleep(2)
                self.queue.task_done()
