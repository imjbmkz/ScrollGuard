import os
from loguru import logger
from pathlib import Path
from pymongo import MongoClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.collection import Collection

ROOT_DIRECTORY = Path(__file__).parent.parent.parent

def get_config() -> Collection:
    # ====================
    # Transfer config from config.json to Mongo
    # ====================
    # with open(CONFIG_PATH) as fp:
    #     return json.load(fp)
    client = get_mongo_cloud_client()
    db = client["scrollguard"]
    return db["CONFIG"]
    
def get_mongo_client() -> MongoClient:
    host = os.environ["MONGO_HOST"]
    return MongoClient(host=host)

def get_mongo_cloud_client() -> MongoClient:
    # Create a new client and connect to the server
    uri = os.environ["MONGO_CLIENT"]
    client = MongoClient(uri, server_api=ServerApi('1'))
    return client

def get_logger() -> logger:
    lg = logger
    lg.add(ROOT_DIRECTORY / "logs/out.log", level="INFO")
    lg.add(ROOT_DIRECTORY / "logs/err.log", level="ERROR")
    return lg