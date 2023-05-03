import tweepy
import plotly.graph_objs as go
from plotly.subplots import make_subplots
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

# Create a Plotly graph
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(x=date_list, y=followers_list, mode='lines', name='Followers'))

fig.update_layout(title=f'Twitter Followers Over Time for @{screen_name}', showlegend=True)
fig.update_xaxes(title_text='Date')
fig.update_yaxes(title_text='Followers', secondary_y=False)

# Save the graph as an HTML file
if not os.path.exists("graphs"):
    os.mkdir("graphs")

graph_filename = f"graphs/{screen_name}_followers_over_time.html"
fig.write_html(graph_filename)
