from scrollguard.utils import get_config, get_logger
from scrollguard.etl import *

if __name__=="__main__":
    logger = get_logger()
    logger.info("ScrollGuard ETL pipeline has started.")

    # Get the appropriate function based on source format
    func_map = {
        "CSV": extract_csv,
        "EXCEL": extract_excel,
        "XML": extract_xml
    }
    config = get_config()["SOURCES"]

    ##################################
    # STEP 1: DOWNLOAD RAW SOURCES
    ##################################

    # Iterate through the registered sources
    for source_name, conf in config.items():
        source_format = conf["FORMAT"]

        # Get appropriate extract function
        try:
            extract_func = func_map[source_format]
            # Extract data
            try:
                logger.info(f"Extracting {source_name}.")
                data = extract_func(conf)
                # Load to MongoDB
                try:
                    logger.info(f"Loading {source_name} to database.")
                    load_to_mongo(f"{source_name}_RAW", data)
                except Exception as e:
                    logger.error(f"An error has occured in loading {source_name} data to MongoDB. {e}")

            except Exception as e:
                logger.error(f"An error has occured in parsing {source_name}. {e}")

        except Exception as e:
            logger.error(f"There is no registered parser for file format {source_format}. {e}")

    ##################################
    # STEP 2: APPLY PREPROCESSING STEPS
    ##################################
    clean_sources = get_config()["TRANSFORM"].keys()
    clean_dfs = []
    for clean_source in clean_sources:
        # Apply data transformer based on configuration 
        clean_data = Transformer(source_name=clean_source, transform=True).processed_data
        clean_dfs.append(clean_data)
        # Load to MongoDB
        try:
            logger.info(f"Loading {clean_source} to database.")
            load_to_mongo(f"{clean_source}_CLEAN", clean_data)
        except Exception as e:
            logger.error(f"An error has occured in loading {clean_source} data to MongoDB. {e}")

    # Consolidate clean sanction sources
    consolidated = append_data(clean_dfs)
    load_to_mongo("CONSOLIDATED_SANCTIONS", consolidated)