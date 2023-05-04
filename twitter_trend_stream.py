import os
import tweepy
import random
import queue
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

api_key = os.getenv("API_KEY", "")
api_secret_key = os.getenv("API_SECRET_KEY", "")
access_token = os.getenv("ACCESS_TOKEN", "")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET", "")

auth = tweepy.OAuth1UserHandler(
    api_key, api_secret_key, access_token, access_token_secret
)

api = tweepy.API(auth)
screen_name = "lil_bigsky_agi"

la_trend = api.get_place_trends(id=2442047)
print('LOS ANGELES TRENDS')
for i in range(10):
    print(la_trend[0]["trends"][i]["name"])

sf_trend = api.get_place_trends(id=2487956)
print('SF TRENDS')
for i in range(40):
    print(sf_trend[0]["trends"][i]["name"])

nyc_trend = api.get_place_trends(id=2459115)
print('NYC TRENDS')
for i in range(10):
    print(nyc_trend[0]["trends"][i]["name"])
