from collector import token_collector
from exceptions.exceptions import *
from evaluation.evaluator import Evaluator
import evaluation.evaluation_config
import pymongo
import logging
import math
from dotenv import load_dotenv
import os

load_dotenv()


logger = logging.getLogger(__name__)
handler = logging.FileHandler(f"logs/{__name__}_log.log")
formatter = logging.Formatter('%(asctime)s : %(levelname)s :  %(name)s  : %(funcName)s : %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

db_client = pymongo.MongoClient(os.getenv('MONGODB_INSTANCE'))
scam_db = db_client['eth-scam-checker']
manual_scam_db = db_client['manual-eth-scam-checker']
scan_history_db = db_client['scan-history']


def analyse_token(token):
    scanned_token_entry = token_collector.collect_token_details(token)

    # config = {
    #     "score_liquidity_share": evaluation.evaluation_config.score_liquidity_share,
    #     "score_holder_share": evaluation.evaluation_config.score_holder_share,
    #     "score_liquidity_amount": evaluation.evaluation_config.score_liquidity_amount,
    #     "score_vulnerabilities": evaluation.evaluation_config.score_vulnerabilities
    # }

    evaluator = Evaluator(scanned_token_entry, evaluation.evaluation_config.DEFAULT_CONFIG)
    indicator_results, final_score = evaluator.get_score()

    custom_scam_result, custom_scam_probability = evaluator.get_custom_scam_result()

    scanned_token_entry["indicator_results"] = indicator_results
    scanned_token_entry["combined_score"] = final_score

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

    manual_scam_db.scanned_tokens.replace_one({"address": token}, scanned_token_entry, upsert=True)
    scan_history_db.scanned_tokens.insert_one(scanned_token_entry)
    scanned_token_entry.pop("_id")
    logger.info(f"Inserting {token} into {manual_scam_db.name}.{manual_scam_db.scanned_tokens.name}")

    return scanned_token_entry


def get_token_from_monitor(token):
    result = scam_db.scanned_tokens.find_one({"address": token}, {"_id": 0})

    return result


def get_scan_history(token):
    result = []
    query = scan_history_db.scanned_tokens.find({"address": token}, {"_id": 0,
                                                                     "address": 1,
                                                                     "scan_time": 1,
                                                                     "custom_scam_probability": 1,
                                                                     "svm_scam_probability": 1,
                                                                     "xgboost_scam_probability": 1,
                                                                     "liquidity_amount.eth_liquidity": 1
                                                                     }).sort("scan_time", pymongo.DESCENDING)

    for scan in query:
        result.append({
            "address": scan["address"],
            "scan_time": scan["scan_time"],
            "custom_scam_probability": scan["custom_scam_probability"],
            "svm_scam_probability": scan["svm_scam_probability"],
            "xgboost_scam_probability": scan["xgboost_scam_probability"],
            "liquidity_amount": float(scan["liquidity_amount"]["eth_liquidity"]),
        })
    return result


def get_recent_from_monitor(page_num, page_size):
    documents_in_db = scam_db.scanned_tokens.count_documents({})

    if page_size < 1:
        page_size = 1

    if page_num < 0:
        page_num = 0

    start = page_num * page_size
    end = start + page_size
    total_pages = math.ceil(documents_in_db / page_size)

    if end > documents_in_db:
        start = documents_in_db - page_size

    query = scam_db.scanned_tokens.find({}, {"_id": 0}).sort("scan_time", pymongo.DESCENDING).skip(start).limit(
        page_size)
    result = []
    for token in query:
        try:
            custom_score = token['custom_scam_probability']
            svm_score = token['svm_scam_probability']
            xgb_score = token['xgboost_scam_probability']

        except:
            custom_score = None
            svm_score = None
            xgb_score = None

        result.append({
            "address": token['address'],
            "scan_time": token['scan_time'],
            "name": token['name'],
            "symbol": token['symbol'],
            "custom_score": custom_score,
            "svm_score": svm_score,
            "xgb_score": xgb_score
        })

    result.append({"pagination": {"maxItems": documents_in_db,
                                  "pageSize": page_size,
                                  "pageNum": page_num,
                                  "totalPages": total_pages}})

    return result


def get_token_from_submission(token):
    result = manual_scam_db.scanned_tokens.find_one({"address": token}, {"_id": 0})

    return result
