import os
import tweepy
import pytz
from dotenv import load_dotenv
from datetime import datetime, timedelta
import requests
import twitter_actions
import urllib.request, json, requests, time

load_dotenv()

giphy_api_key = os.getenv("GIPHY_API", "")
CONSUMER_KEY = os.getenv("API_KEY", "")
CONSUMER_SECRET = os.getenv("API_SECRET_KEY", "")
ACCESS_KEY = os.getenv("ACCESS_TOKEN", "")
ACCESS_SECRET = os.getenv("ACCESS_TOKEN_SECRET", "")

def modifier(s):
    '''
    returns hashtags based on the GIF names from GIPHY
    '''
    ms =''
    for i in range(len(s)):
        if(s[i]=='-'):
            ms+=' '
        else:
            ms+=s[i]
    ls = ms.split()
    del ls[-1]
    ls[0] = "#" + ls[0]
    return (" #".join(ls))

def gif_download(gif_url):
    '''
    Takes the URL of an Image/GIF and downloads it
    '''
    gif_data = requests.get(gif_url).content
    with open('image.gif', 'wb') as handler:
        handler.write(gif_data)
        handler.close()

def tweet(tweet_msg):
    message= tweet_msg + " #funny #gif #lol #humor" #TODO: Add desired tweet message here
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
    api.update_with_media('image.gif', status=message)


def gif_post(gif_url_list, msg):
    """
    tweets GIFs and sleeps for a specific time
    """
    for i in range(len(gif_url_list)):
        try:
            gif_download(gif_url_list[i])
            m = modifier(msg[i])
            tweet(m)
        except:
            continue
        time.sleep(900) #TODO: Change this number to modify how often each tweet gets posted

while True:

    giphy_url = "http://api.giphy.com/v1/gifs/trending?&api_key="+giphy_api_key+"&limit=10"

    with urllib.request.urlopen(giphy_url) as response:
       html = response.read()

    h=html.decode("utf-8")
    gif_info = json.loads(h)
    gif_data = gif_info["data"]
    gif_urls = []
    slugs = []

    for i in range(len(gif_data)):
        gif = gif_data[i]['images']["downsized"]["url"]
        slug = gif_data[i]['slug']
        gif_urls.append(gif)
        slugs.append(slug)

    gif_post(gif_urls, slugs)
    print("TWEETING GIF")
    gif_urls = []
    slugs = []
