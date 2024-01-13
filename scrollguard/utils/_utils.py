import os
import json
from loguru import logger
from pathlib import Path
from pymongo import MongoClient

ROOT_DIRECTORY = Path(__file__).parent.parent.parent
CONFIG_PATH = ROOT_DIRECTORY / "config.json"

def get_config() -> dict:
    with open(CONFIG_PATH) as fp:
        return json.load(fp)
    
def get_mongo_client() -> MongoClient:
    host = os.environ["MONGO_HOST"]
    return MongoClient(host=host)

def get_logger() -> logger:
    lg = logger
    lg.add(ROOT_DIRECTORY / "logs/out.log", level="INFO")
    lg.add(ROOT_DIRECTORY / "logs/err.log", level="ERROR")
    return lg