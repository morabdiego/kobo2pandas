import os
from dotenv import load_dotenv
from kobo2pandas import KoboAPI
import pandas as pd

load_dotenv()
API_KEY = os.getenv("API_KEY")
client = KoboAPI(token=API_KEY)
survey_uid = client.list_uid()['simple']

assets = client.list_assets()
asset = client.get_asset(asset_uid=survey_uid)
questions = client.get_questions(asset)
choices = client.get_choices(asset)
survey = client.get_data(survey_uid)

print(asset, questions, choices, survey, assets)
