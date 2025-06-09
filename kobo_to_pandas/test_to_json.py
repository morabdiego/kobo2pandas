import os
import json
from dotenv import load_dotenv
from app import KoboAPI
from pprint import pprint

load_dotenv()
API_KEY = os.getenv("API_KEY")
client = KoboAPI(token=API_KEY)

uid = client.list_uid()['simple']
survey = client.get_asset(asset_uid=uid)
data = client.get_data(uid)

with open('./data/data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
