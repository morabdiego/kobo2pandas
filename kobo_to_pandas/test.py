import os
from dotenv import load_dotenv
from .api.koboapi import KoboAPI

load_dotenv()
API_KEY = os.getenv("API_KEY")
client = KoboAPI(token=API_KEY, debug=True)

uid = client.list_uid()['simple']
survey = client.get_asset(asset_uid=uid)
