import requests
import urllib3
import ssl
import pandas as pd
import xmltodict

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

def extract_csv(config: dict) -> pd.DataFrame:
    """ Pass the source configuration from config.json 
        {source_name: source_config}
    """
    url = config["URL"]
    params = config["PARAMS"]
    return pd.read_csv(url, **params)

def extract_xml(config: dict) -> dict:
    """ Pass the source configuration from config.json 
        {source_name: source_config}
    """
    url = config["URL"]

    try:
        # Try a normal GET request
        response = requests.get(url)
    except:
        try:
            # Try the request with custom adapter 
            response = get_legacy_session().get(url)
        except:
            raise Exception(f"An error has occurred when sending request to {url}.")

    if response.ok:
        return xmltodict.parse(response.content)
    
    else:
        raise Exception(f"An error has occurred when sending request to {url}. {response.status_code}")