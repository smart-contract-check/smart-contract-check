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
import pymongo
from web3 import Web3
from evaluation.evaluator import Evaluator
import evaluation.evaluation_config
import pandas as pd
import json
from collector import token_collector
from dotenv import load_dotenv
import os

load_dotenv(".env")

logger = logging.getLogger(__name__)

db_client = pymongo.MongoClient(os.getenv('MONGODB_INSTANCE'))
scam_db = db_client["eth-scam-checker"]


def cleanup_statistics_db():
    db_client.drop_database('statistics')


def prepare_statistics_from_existing(source_db, target_db, dataset):
    for index, entry in dataset.iterrows():
        token_address = Web3.toChecksumAddress(entry['address'])
        token = source_db.scanned_tokens.find_one({'address': token_address}, {"_id": 0})

        if token is None:
            token_in_statistics = target_db.scanned_tokens.find_one({'address': token_address})
            last_scanned = -999999

            if token_in_statistics is not None:
                last_scanned = token_in_statistics['scan_time'] - time.time()

            if last_scanned > -1200:
                continue

            logger.info(f"collecting {token_address}")
            token = token_collector.collect_token_details(token_address)

        logger.info(f"Inserting {token_address}")
        target_db.scanned_tokens.replace_one({"address": token_address}, token, upsert=True)


def prepare_statistics_rescan(target_db, dataset):
    for index, entry in dataset.iterrows():
        token_address = Web3.toChecksumAddress(entry['address'])

        token_already_scanned = target_db.scanned_tokens.find_one({'address': token_address}, {"_id": 0})
        last_scanned = -9999999

        if token_already_scanned is not None:
            last_scanned = token_already_scanned['scan_time'] - time.time()

        if last_scanned > -4000:
            continue

        logger.info(f"collecting {token_address}")
        token = token_collector.collect_token_details(token_address)

        logger.info(f"Inserting {token_address}")
        target_db.scanned_tokens.replace_one({"address": token_address}, token, upsert=True)


def evaluate_dataset(statistics_database, dataset):

    accuracy_results = {}
    indicator_results = ["liquidity_share_result",
                         "holder_share_result",
                         "liquidity_amount_result",
                         "honeypot_result",
                         "ownership_result",
                         "verified_contract_result",
                         "vulnerabilities_result"
                         ]

    for ir in indicator_results:
        accuracy_results[ir] = {}

    total_accuracy = {
            "tp": 0,
            "fn": 0,
            "fp": 0,
            "tn": 0,
            "undecided": 0,
            "uk": 0,
    }
    total_accuracy_classifier = {
            "tp": 0,
            "fn": 0,
            "fp": 0,
            "tn": 0,
            "undecided": 0,
            "uk": 0,
    }

    final_results = []

    for ir in indicator_results:
        accuracy_results[ir]['tp'] = 0
        accuracy_results[ir]['fn'] = 0
        accuracy_results[ir]['fp'] = 0
        accuracy_results[ir]['tn'] = 0
        accuracy_results[ir]['undecided'] = 0
        accuracy_results[ir]['unknown'] = 0

    for index, entry in dataset.iterrows():
        token = statistics_database.scanned_tokens.find_one({'address': Web3.toChecksumAddress(entry['address'])})
        if token is None:
            print(entry['address'])
        evaluator = Evaluator(token, evaluation.evaluation_config.DEFAULT_CONFIG)
        result, final_result = evaluator.get_score()

        guess, proba = evaluator.get_custom_scam_result()
        # print(proba)
        # print(guess)
        # print(entry['Scam'])

        annotation = entry['Scam']

        if annotation == 1.0:
            for key in result.keys():
                if result[key] is None:
                    accuracy_results[key]['unknown'] += 1
                    logger.warning(f"Indicator {key} has None, skipped")
                elif result[key] > 0.5:
                    accuracy_results[key]['tp'] += 1
                elif result[key] == 0.5:
                    accuracy_results[key]['undecided'] += 1
                else:
                    accuracy_results[key]['fn'] += 1
        else:
            for key in result.keys():
                if result[key] is None:
                    accuracy_results[key]['unknown'] += 1
                    logger.warning(f"Indicator {key} has None, skipped")
                elif result[key] > 0.5:
                    accuracy_results[key]['fp'] += 1
                elif result[key] == 0.5:
                    accuracy_results[key]['undecided'] += 1
                else:
                    accuracy_results[key]['tn'] += 1

        if annotation == 1:
            if final_result > 0.58:
                total_accuracy['tp'] += 1
            elif final_result <= 0.58:
                total_accuracy['fn'] += 1
            else:
                total_accuracy['uk'] += 1
        else:
            if final_result > 0.58:
                total_accuracy['fp'] += 1
            elif final_result <= 0.58:
                total_accuracy['tn'] += 1
            else:
                total_accuracy['uk'] += 1

        if annotation == 1:
            if guess == 1:
                total_accuracy_classifier['tp'] += 1
            else:
                total_accuracy_classifier['fn'] += 1
        else:
            if guess == 1:
                total_accuracy_classifier['fp'] += 1
            else:
                total_accuracy_classifier['tn'] += 1

        final_results.append((final_result, annotation))

        # print(token['address'])
        # print(annotation)
        # print(final_result)

        # print(json.dumps(result, indent=4))
        # print(json.dumps(accuracy_results, indent=4))

    print(json.dumps(accuracy_results, indent=4))
    # print(final_results)

    print(json.dumps(total_accuracy, indent=4))
    print(json.dumps(total_accuracy_classifier, indent=4))

    accuracy = (total_accuracy['tp'] + total_accuracy['tn']) / len(final_results)
    precision = total_accuracy['tp'] / (total_accuracy['tp'] + total_accuracy['fp'])
    recall = total_accuracy['tp'] / (total_accuracy['tp'] + total_accuracy['fn'])

    f1_score = 2 * (precision * recall) / (precision + recall)

    print(f"accuracy: {accuracy}")
    print(f"percision: {precision}")
    print(f"recall: {recall}")
    print(f"F1 Score: {f1_score}")


    # test_results = scam_db.scanned_tokens.find()
    # for token in test_results:
    #     evaluator = Evaluator(token, config)
    #     result = evaluator.get_score()
    #     print(token['address'])
    #     print(result)


def evaluate_dataset_with_classifier(statistics_database, dataset):
    for index, entry in dataset.iterrows():
        token = statistics_database.scanned_tokens.find_one({'address': Web3.toChecksumAddress(entry['address'])})

        evaluator = Evaluator(token, evaluation.evaluation_config.DEFAULT_CONFIG)
        result, final_result = evaluator.get_score()

        [guess], [proba] = evaluator.get_scam_result()


if __name__ == '__main__':

    statistics_db = db_client['statistics']
    statistics_rescan_db = db_client['statistics-rescan']

    big_dataset_db = db_client['statistics-big-dataset']
    big_dataset_rescan_db = db_client['statistics-big-dataset-rescan']

    big_dataset_with_legit_db = db_client['statistics-big-legit-dataset']
    big_dataset_with_legit_rescan_db = db_client['statistics-big-legit-dataset-rescan']

    random_old_db = db_client['random-old-dataset']
    random_old_rescan_db = db_client['random-old-dataset-rescan']
    smoke_test_db = db_client['smoke-test-eth-scam-checker']

    big_dataset_50_50 = db_client['big-dataset-50-50']
    big_dataset_50_50_rescan = db_client['big-dataset-50-50-rescan']
    big_dataset_50_50_rescan2 = db_client['big-dataset-50-50-rescan-2']

    testset_db = db_client['testset-db']
    testset_rescan_db = db_client['testset-rescan-db']

    dataset_file = "./data/first_dataset.CSV"
    data = pd.read_csv(dataset_file)

    dataset2_file = "./data/big_dataset_annotated.csv"
    data2 = pd.read_csv(dataset2_file)

    dataset3_file = "./data/big_dataset_annotated_with_legit.csv"
    data3 = pd.read_csv(dataset3_file)

    dataset4_file = "./data/random_tokens_annotated.csv"
    data4 = pd.read_csv(dataset4_file)

    dataset5_file = "./data/big_dataset_50_50.csv"
    data5 = pd.read_csv(dataset5_file)

    dataset_testset_file = "./data/test_dataset.CSV"
    data_testset = pd.read_csv(dataset_testset_file)

    # prepare_statistics_from_existing(scam_db, statistics_db, data)
    # prepare_statistics_rescan(statistics_rescan_db, data)

    # evaluate_dataset(statistics_db, data)
    # evaluate_dataset(statistics_rescan_db, data)


    # prepare_statistics_from_existing(scam_db, big_dataset_db, data2)
    # prepare_statistics_from_existing(scam_db, big_dataset_with_legit_db, data3)
    # prepare_statistics_from_existing(big_dataset_rescan_db, big_dataset_with_legit_rescan_db, data3)
    # prepare_statistics_rescan(big_dataset_rescan_db, data2)

    # prepare_statistics_rescan(testset_rescan_db, data_testset)
    # prepare_statistics_from_existing(scam_db, testset_db, data_testset)

    # prepare_statistics_from_existing(random_old_db, random_old_rescan_db, data4)
    # prepare_statistics_rescan(random_old_rescan_db, data4)
    # prepare_statistics_from_existing(scam_db, big_dataset_50_50, data5)

    # evaluate_dataset(random_old_db, data4)
    # evaluate_dataset(big_dataset_with_legit_db, data3)
    # evaluate_dataset(big_dataset_with_legit_rescan_db, data3)

    evaluate_dataset(big_dataset_50_50, data5)
    # evaluate_dataset(big_dataset_50_50_rescan, data5)
    # evaluate_dataset(big_dataset_50_50_rescan2, data5)

    evaluate_dataset(testset_db, data_testset)
    # evaluate_dataset(testset_rescan_db, data_testset)
    # evaluate_dataset_with_classifier(testset_rescan_db, data_testset)
    # evaluate_dataset_with_classifier(big_dataset_50_50, data5)

    # evaluate_dataset(big_dataset_50_50_rescan2, data_testset)

    # prepare_statistics_rescan(big_dataset_50_50_rescan2, data5)

    # evaluate_dataset(big_dataset_db, data2)
    # evaluate_dataset(big_dataset_rescan_db, data2)


    # evaluate_dataset(statistics_rescan_db, data)
    # evaluate_dataset(statistics_db, data)
    # evaluate_specific_submission("0x1BF0c586176Fd47b2e6285E4293F8B65bcc8Ebff")

    # prepare_statistics_from_existing(scam_db, random_old_rescan_db, data4)
    # prepare_statistics_rescan(random_old_rescan_db, data4)
