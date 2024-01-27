import pandas as pd
from scrollguard.utils import get_config
from scrollguard.etl import *

def extract_data(source_config: dict) -> pd.DataFrame | dict | list:
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

if __name__=="__main__":
    # Get source configuration
    config = get_config().find_one({"source": "SOURCES"}, {"_id":0, "value":1})["value"]

    # Get empty list to store transformed data sources
    consolidated = []

    # Iterate through the registered sources
    for source_name, conf in config.items():
        source_format = conf["FORMAT"]

        # ===========================
        # 1. Extract data from online sources
        # ===========================
        print(f"Extracting {source_name}.")
        data = extract_data(conf)
            
        # ===========================
        # 2. Load raw data to Mongo
        # ===========================
        if "NAMES" in conf.keys():
            for sname, d in zip(conf["NAMES"], data):
                print(f"Loading {sname} to database.")
                load_to_mongo(f"{sname}_RAW", d)
        else:
            print(f"Loading {source_name} to database.")
            load_to_mongo(f"{source_name}_RAW", data)

        # ===========================
        # 3. Apply transformation steps to the raw data, then load clean data to Mongo
        # ===========================
        clean_data = Transformer(source_name, data, True).processed_data
        consolidated.append(clean_data)
        load_to_mongo(f"{source_name}_CLEAN", clean_data)

    # ===========================
    # 4. Consolidate clean sanction sources, then load to Mongo
    # ===========================
    consolidated_df = append_data(consolidated)
    load_to_mongo("CONSOLIDATED_SANCTIONS", consolidated_df)