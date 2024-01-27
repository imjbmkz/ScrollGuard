import pandas as pd
from scrollguard.utils import get_config
from scrollguard.etl import *
from prefect import task, flow

@task
def extract_data(source_config: dict) -> pd.DataFrame | list:
    # Get the appropriate function based on source format
    source_format = source_config["FORMAT"]
    func_map = {
        "CSV": extract_csv,
        "EXCEL": extract_excel,
        "XML": extract_xml
    }
    extract_func = func_map[source_format]

    # For merging multiple sources, return a list of the downloaded data
    if isinstance(source_config["URL"], list):
        urls = source_config["URL"]
        params = source_config["PARAMS"]
        return [extract_func({"URL": url, "PARAMS": param}) for url, param in zip(urls, params)]

    if source_format=="XML": 
        return dict_to_frame(extract_func(source_config))
    
    return extract_func(source_config) 

@task
def transform_data(source_name: str, data: pd.DataFrame) -> pd.DataFrame:
    clean_data = Transformer(source_name, data, True).processed_data
    return clean_data

@flow(log_prints=True)
def pipeline():

    # Get source configuration
    config = get_config().find_one({"source": "SOURCES"}, {"_id":0, "value":1})["value"]

    # Drop consolidated sanctions first
    drop_collection("CONSOLIDATED_SANCTIONS")

    # Iterate through the registered sources
    for source_name, source_config in config.items():

        # ===========================
        # 1. Extract data from online sources
        # ===========================
        print(f"Processing {source_name}.")
        data = extract_data(source_config)

        # ===========================
        # 2. Load raw data to Mongo
        # ===========================
        if "NAMES" in source_config.keys():
            for sname, d in zip(source_config["NAMES"], data):
                load_to_mongo(f"{sname}_RAW", d, True)
        else:
            load_to_mongo(f"{source_name}_RAW", data, True)

        # ===========================
        # 3. Apply transformation steps to the raw data, then load clean data to Mongo
        # ===========================
        clean_data = transform_data(source_name, data)
        load_to_mongo(f"{source_name}_CLEAN", clean_data, True)

        # ===========================
        # 4. Load cleaned data to consolidated sanctions
        # ===========================
        load_to_mongo("CONSOLIDATED_SANCTIONS", clean_data)

if __name__=="__main__":
    pipeline.serve(
        name="scrollguard-etl-pipeline",
        cron="0 21 * * *"
    )