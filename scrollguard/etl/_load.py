import numpy as np
import pandas as pd
from ..utils import get_mongo_cloud_client as get_mongo_client

def load_to_mongo(collection_name: str, data: dict | pd.DataFrame, drop_collection: bool = False):
    """ Load data to database
    """
    # Configure MongoDB destination
    client = get_mongo_client()
    db = client["scrollguard"]
    collection = db[collection_name]
    
    # Convert dataframe to dict 
    if isinstance(data, pd.DataFrame):
        data.replace({np.nan: None}, inplace=True) # Fix on NaT
        data_dict = data.to_dict(orient="records") 
    else: 
        data_dict = data

    # Drop collections first
    if drop_collection:
        collection.drop()

    # Insert data into collection
    collection.insert_many(data_dict) if isinstance(data_dict, list) else collection.insert_one(data_dict)
