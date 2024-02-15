import os
from loguru import logger
from pathlib import Path
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.collection import Collection

ROOT_DIRECTORY = Path(__file__).parent.parent.parent

def get_config() -> Collection:
    client = get_mongo_client()
    db = client["scrollguard"]
    return db["CONFIG"]

def get_mongo_client() -> MongoClient:
    host = os.environ["MONGO_HOST"]
    try:
        return MongoClient(host=host)  
    except:
        return MongoClient(host, server_api=ServerApi('1'))

def get_logger() -> logger:
    lg = logger()
    lg.add(ROOT_DIRECTORY / "logs/out.log", level="INFO")
    lg.add(ROOT_DIRECTORY / "logs/err.log", level="ERROR")
    return lg