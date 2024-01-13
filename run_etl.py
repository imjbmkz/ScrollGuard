from scrollguard.utils import get_config, get_logger
from scrollguard.etl import extract_csv, extract_xml, load_to_mongo

if __name__=="__main__":
    logger = get_logger()
    logger.info("ScrollGuard ETL pipeline has started.")

    # Get the appropriate function based on source format
    func_map = {
        "CSV": extract_csv,
        "XML": extract_xml
    }
    config = get_config()["SOURCES"]

    # Iterate through the registered sources
    for source_name, conf in config.items():
        source_format = conf["FORMAT"]

        # Get appropriate extract function
        try:
            extract_func = func_map[source_format]
            # Extract data
            try:
                data = extract_func(conf)
                # Load to MongoDB
                try:
                    load_to_mongo(source_name, data)
                except Exception as e:
                    logger.error(f"An error has occured in loading {source_name} data to MongoDB. {e}")

            except Exception as e:
                logger.error(f"An error has occured in parsing {source_name}. {e}")

        except Exception as e:
            logger.error(f"There is no registered parser for file format {source_format}. {e}")