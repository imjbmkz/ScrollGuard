import re
import pandas as pd
from functools import reduce
from jellyfish import metaphone
from ..utils import get_config, get_mongo_client
from ..etl import extract_collection

transform_config = get_config()["TRANSFORM"]
general_config = get_config()["GENERAL"]
MIN_NAME_LENGTH = general_config["MIN_NAME_LENGTH"]

class HmTransformer:
    def __init__(self, transform: bool = True):
        self.raw_data = extract_collection("HM")
        self.processed_data = self.raw_data
        self.config = transform_config["HM"]
        self.transform = transform
        if self.transform:
            self.select_required_fields()
            self.get_transformed_names()    

    def select_required_fields(self):
        self.processed_data = select_fields(self.raw_data, self.config["SELECT_FIELDS"])

    def get_transformed_names(self):
        self.processed_data["STANDARDIZED_NAME"] = self.processed_data["FULL_NAME"].map(standardize_name)
        self.processed_data["METAPHONE_NAME"] = self.processed_data["STANDARDIZED_NAME"].map(metaphone_name)

def standardize_name(fullname: str) -> str:
    std_name = re.sub("-|/", " ", str(fullname).upper())  # replace - and / with space
    std_name = re.sub("[^A-Z0-9 ]+", "", std_name)  # select alphanumeric and space
    std_name = re.sub(" +", " ", std_name).strip()  # remove multiple spaces

    if len(std_name)>=MIN_NAME_LENGTH:
        return std_name
    
def metaphone_name(standardized_name: str) -> str:
    if pd.notna(standardized_name) and isinstance(standardized_name, str):
        return metaphone(standardized_name)

def merge_data(dfs: list, join_key: str) -> pd.DataFrame:
    merged_data = reduce(lambda left, right: pd.merge(left, right, on=join_key, how="left"), dfs)
    return merged_data

def select_fields(data: pd.DataFrame, config: dict) -> pd.DataFrame:
    data_transformed = data.copy()
    new_columns = list(config.keys())
    
    for key, value in config.items():
        if isinstance(value, list):
            # Concatenate columns if list of columns is supplied
            data_transformed[key] = data_transformed[value].apply(lambda row: " ".join(row.fillna("").values.astype(str)).strip(), axis=1)
        else:
            # Rename the column
            data_transformed.rename(columns={value:key}, inplace=True)

    data_transformed = data_transformed[new_columns]
    return data_transformed

