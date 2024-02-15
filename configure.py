import json
from scrollguard.utils import get_mongo_client

if __name__=="__main__":

    client = get_mongo_client()
    db = client["scrollguard"]
    db.drop_collection("CONFIG")

    with open("config.json", "rb") as fp:
        config = json.load(fp)

    col = db["CONFIG"]
    col.insert_many(config)

    print("Initial configurations have already been set.")