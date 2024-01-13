import pandas as pd
from ..utils import get_mongo_client

def load_to_mongo(collection_name: str, data: dict | pd.DataFrame):
    """ Load data to database
    """
    # Configure MongoDB destination
    client = get_mongo_client()
    db = client["scrollguard"]
    collection = db[collection_name]
    
    # Convert dataframe to dict 
    data_dict = data.to_dict(orient="records") if isinstance(data, pd.DataFrame) else data

    # Drop collections first
    collection.drop()

    # Insert data into collection
    collection.insert_many(data_dict) if isinstance(data_dict, list) else collection.insert_one(data_dict)