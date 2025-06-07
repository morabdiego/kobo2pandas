import os
import json
from dotenv import load_dotenv
from app import KoboAPI

load_dotenv()
API_KEY = os.getenv("API_KEY")
client = KoboAPI(token=API_KEY, debug=True)

uid = client.list_uid()['simple']
survey = client.get_asset(asset_uid=uid)['content']['survey']

# Export survey as JSON to data folder
with open('./data/asset.json', 'w', encoding='utf-8') as f:
    json.dump(survey, f, indent=2, ensure_ascii=False)
