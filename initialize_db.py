import pymongo
import datetime
from pymongo.errors import *
from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()

db_client = pymongo.MongoClient(os.getenv('MONGODB_INSTANCE'))
scam_db = db_client["eth-scam-checker"]
manual_scam_db = db_client["manual-eth-scam-checker"]
pairs_collection = scam_db["pairs"]
scanned_tokens_collection = scam_db["scanned_tokens"]
manual_scanned_tokens_collection = manual_scam_db["scanned_tokens"]
scan_history_db = db_client['scan-history']


def initialize_db():
    pairs_collection.create_index("pair_address", unique=True)

    scanned_tokens_collection.create_index("address", unique=True)
    scanned_tokens_collection.create_index("scan_time")

    manual_scanned_tokens_collection.create_index("address", unique=True)
    manual_scanned_tokens_collection.create_index("scan_time")

    scan_history_db.scanned_tokens.create_index("address")
    scan_history_db.scanned_tokens.create_index("scan_time")


def main():
    initialize_db()


if __name__ == '__main__':
    main()
