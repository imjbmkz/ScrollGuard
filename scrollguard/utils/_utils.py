import os
from loguru import logger
from pathlib import Path
from pymongo import MongoClient
from pymongo.collection import Collection

ROOT_DIRECTORY = Path(__file__).parent.parent.parent

def get_config() -> Collection:
    # ====================
    # Transfer config from config.json to Mongo
    # ====================
    # with open(CONFIG_PATH) as fp:
    #     return json.load(fp)
    client = get_mongo_client()
    db = client["scrollguard"]
    return db["CONFIG"]
    
def get_mongo_client() -> MongoClient:
    host = os.environ["MONGO_HOST"]
    return MongoClient(host=host)

def get_logger() -> logger:
    lg = logger
    lg.add(ROOT_DIRECTORY / "logs/out.log", level="INFO")
    lg.add(ROOT_DIRECTORY / "logs/err.log", level="ERROR")
    return lg