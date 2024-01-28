import re
import pandas as pd
from functools import reduce
from jellyfish import metaphone
from ..utils import get_config, get_mongo_cloud_client as get_mongo_client

source_config = get_config().find_one({"source": "SOURCES"}, {"_id":0, "value":1})["value"]
general_config = get_config().find_one({"source": "GENERAL"}, {"_id":0, "value":1})["value"]
MIN_NAME_LENGTH = general_config["MIN_NAME_LENGTH"]

class Transformer:
    def __init__(self, source_name: str, data: dict | pd.DataFrame | list, transform: bool = False):
        # Get configuration
        self.source_name = source_name
        self.config = source_config[source_name]
        self.raw_data = data

        if transform:
            self.transform_data()

    def transform_data(self):
        self.processed_data = self.raw_data
        for step_name, step_config in self.config["STEPS"].items():
            if step_name=="MERGE_DATASETS":
                self.processed_data = merge_data(self.processed_data, step_config["JOIN_KEY"])

            elif step_name=="SELECT_FIELDS":
                self.processed_data = select_fields(self.processed_data, step_config)

            elif step_name=="ADD_COLUMNS":
                for key, value in step_config.items():
                    self.processed_data[key] = value

            elif step_name=="PARSE_COLUMN":
                for key, value in step_config.items():
                    parsed = parse_column(data=self.raw_data[list(value.values())[0:2]],**{k.lower():v for k,v in value.items()})
                    self.processed_data = self.processed_data.merge(parsed, how="left", left_on="ID", right_on=value["REFERENCE"])
                    self.processed_data.drop(value["REFERENCE"], axis=1, inplace=True)
                    self.processed_data.rename(columns={value["TARGET_COLUMN"]:key}, inplace=True)

        # Add preprocessed names
        self.processed_data["STANDARDIZED_NAME"] = self.processed_data["FULL_NAME"].map(standardize_name)
        self.processed_data["METAPHONE_NAME"] = self.processed_data["STANDARDIZED_NAME"].map(metaphone_name)

        # Add source name
        self.processed_data.insert(0, "SOURCE_NAME", self.source_name)
        self.processed_data.drop_duplicates(inplace=True)

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

def append_data(dfs: list) -> pd.DataFrame:
    return pd.concat(dfs, ignore_index=True).drop_duplicates()

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

def dict_to_frame(data: dict | list) -> pd.DataFrame:
    try:
        return pd.DataFrame(data)
    except:
        return pd.DataFrame([data])    

def parse_column(data: pd.DataFrame, reference: str, column_to_parse: str, target_column: str) -> pd.DataFrame:
    dfs = []
    for _, row in data[data[column_to_parse].notna()][[reference,column_to_parse]].iterrows():
        d = dict_to_frame(row[column_to_parse])
        d.insert(0, reference, row[reference])
        dfs.append(d)
    parsed = pd.concat(dfs)[[reference, target_column]].drop_duplicates(ignore_index=True)
    return parsed.dropna()

def drop_collection(collection: str):
    client = get_mongo_client()
    db = client["scrollguard"]
    db.drop_collection(collection)