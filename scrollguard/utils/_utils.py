import os
import json
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