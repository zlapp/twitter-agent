import tweepy
import matplotlib.pyplot as plt
import datetime
import os
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

user = api.get_user(screen_name=screen_name)
followers_count = user.followers_count
print(followers_count)
created_at = user.created_at

date_list = []
followers_list = []

for status in tweepy.Cursor(api.user_timeline, tweet_mode='extended').items():
    date_list.append(status.created_at)
    followers_list.append(status.user.followers_count)

# Create a matplotlib graph
plt.figure(figsize=(12, 6))
plt.plot(date_list, followers_list)
plt.xlabel('Date')
plt.ylabel('Followers')
plt.title(f'Twitter Followers Over Time for @{screen_name}')
plt.grid()

# Save the graph as a PNG file
if not os.path.exists("graphs"):
    os.mkdir("graphs")

graph_filename = f"graphs/{screen_name}_followers_over_time.png"
plt.savefig(graph_filename, dpi=300)
plt.close()
