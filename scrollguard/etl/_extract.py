import requests
import urllib3
import ssl
import pandas as pd
import xmltodict
from pathlib import Path
from ..utils import get_mongo_client, ROOT_DIRECTORY

""" 
OTHER SOURCES TO CONSIDER: 
    - https://sanctionscanner.com/blog/what-is-a-sanction-list-8
    - https://github.com/moov-io/watchman
"""

""" BEGIN SECTION
ISSUE: SSLError when downloading UN source via requests
ERROR: SSLError: HTTPSConnectionPool(host='scsanctions.un.org', port=443): 
    Max retries exceeded with url: /resources/xml/en/consolidated.xml 
    (Caused by SSLError(SSLError(1, '[SSL: UNSAFE_LEGACY_RENEGOTIATION_DISABLED] 
    unsafe legacy renegotiation disabled (_ssl.c:1007)')))
DESCRIPTION: Encounters this issue on WSL2 Ubuntu 22.04.3 LTS (jammy), 
    but not on regular Windows machine.
SOURCE: https://stackoverflow.com/a/73519818
"""
class CustomHttpAdapter (requests.adapters.HTTPAdapter):
    # "Transport adapter" that allows us to use custom ssl_context.
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_context=self.ssl_context)

def get_legacy_session():
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
    session = requests.session()
    session.mount("https://", CustomHttpAdapter(ctx))
    return session

""" END SECTION
"""

def download_file(url: str, file_path: str | Path = None, 
                  save_file: bool = False) -> None | requests.Response:
    # Raise an error when file_path is not supplied, but save_file
    if file_path is None and save_file:
        raise ValueError("File is expected to be downloaded, but no file_path supplied.")
    
    try:
        # Try a normal GET request
        response = requests.get(url)
    except:
        try:
            # Try the request with custom adapter 
            response = get_legacy_session().get(url)
        except:
            raise Exception(f"An error has occurred when sending request to {url}.")
    
    # Download the file if save_file=True. Otherwise, just return the response.
    if not save_file:
        return response
    with open(file_path, "wb") as fp:
        fp.write(response.content)

def extract_csv(config: dict) -> pd.DataFrame:
    # Set variables
    url = config["URL"]
    source_name = config["NAME"]
    source_format = config["FORMAT"]
    params = config["PARAMS"]
    file_path = ROOT_DIRECTORY / f"data/raw/{source_name}.{source_format}"
    
    # Download the file first to data/raw
    download_file(url, file_path, save_file=True)

    # Return dataframe
    return pd.read_csv(file_path, **params)

def extract_excel(config: dict) -> pd.DataFrame:
    # Set variables
    url = config["URL"]
    source_name = config["NAME"]
    source_format = config["FORMAT"]
    params = config["PARAMS"]
    file_path = ROOT_DIRECTORY / f"data/raw/{source_name}.{source_format}"
    
    # Download the file first to data/raw
    download_file(url, file_path, save_file=True)

    # Return dataframe
    return pd.read_excel(file_path, **params)

def extract_xml(config: dict) -> dict:
    """ Pass the source configuration from config.json 
        {source_name: source_config}
    """
    # Set variables
    url = config["URL"]
    source_name = config["NAME"]
    source_format = config["FORMAT"]
    file_path = ROOT_DIRECTORY / f"data/raw/{source_name}.{source_format}"
    
    # Download the file first to data/raw
    download_file(url, file_path, save_file=True)

    # Return dict
    with open(file_path, "rb") as fp:
        return xmltodict.parse(fp)
    
def extract_collection(collection_name: str, database: str = "scrollguard") -> pd.DataFrame:
    client = get_mongo_client()
    db = client[database]
    collection = db[collection_name]
    return pd.DataFrame(collection.find({}, {"_id": 0}))