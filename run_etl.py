from scrollguard.utils import get_config
from scrollguard.etl import extract_csv, extract_xml

config = get_config()["SOURCES"]

for source_name, conf in config.items():

    if source_name=="UN":

        if conf["FORMAT"]=="CSV":
            data = extract_csv(conf)

        elif conf["FORMAT"]=="XML":
            data = extract_xml(conf)

        print(data.keys())
        print("Success")
