import os
import re
import tweepy
import random
import pytz
import yaml
from dotenv import load_dotenv
from datetime import datetime, timedelta
import requests
import urllib.request, json, requests, time
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
giphy_api_key = os.getenv("GIPHY_API", "")
CONSUMER_KEY = os.getenv("API_KEY", "")
CONSUMER_SECRET = os.getenv("API_SECRET_KEY", "")
ACCESS_KEY = os.getenv("ACCESS_TOKEN", "")
ACCESS_SECRET = os.getenv("ACCESS_TOKEN_SECRET", "")

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

with open("params.yaml", "r") as file:
    params = yaml.safe_load(file)

llm = OpenAI(temperature=0.9)
gif_prompt = PromptTemplate(
    input_variables=["input_text"],
    template="You are a GIF search agent.  Based on the: {input_text} return four keywords as a single line like `hello world sexy hello`. Do not use line breaks, or commas. Your goal is to find a funny gif to match the input.  Sexy and funny is best",
)
gif_chain = LLMChain(llm=llm, prompt=gif_prompt)

reply_prompt = PromptTemplate(
    input_variables=["input_text"],
    template="You are a tweet reply agent.  You are replying to a tweet that says: {input_text}.  Make sure the reply is under 140 characters.  Be sarcastic and funny.",
)
reply_chain = LLMChain(llm=llm, prompt=reply_prompt)

def generate_response(input_text):
    # Use the input_text to generate a response using your Language Model
    # For example, using OpenAI's GPT-3
    response = reply_chain.run(input_text=input_text)
    return response

def should_respond():
    return random.random() <= params["gif_respond_probability"]  # 5% probability of returning True

def generate_response(tweet):
    # Generate a response using your LLM agent based on the context of the tweet
    response = reply_chain.run(tweet.text)  # Replace this with your actual LLM-generated response
    print(f"Responding to {tweet.user.screen_name}: {tweet.text}")
    return response

def respond_to_timeline_tweets():
    timeline_tweets = api.home_timeline(count=100)  # Fetch 100 most recent tweets from your timeline
    my_screen_name = 'lil_bigsky_agi'  # Fetch your account's screen_name

    for tweet in timeline_tweets:
        if tweet.user.screen_name != my_screen_name and should_respond():
            response = generate_response(tweet)
            keywords_search = gif_chain.run(input_text=response)
            search_gif(keywords_search, response)
            result = api.media_upload('image.gif')
            api.update_status('@{} {}'.format(tweet.user.screen_name, response), in_reply_to_status_id=tweet.id, media_ids=[result.media_id_string])

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

def tweet(tweet_msg, response):
   # auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
   # auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
   # api = tweepy.API(auth)

    result = api.media_upload('image.gif')
    #res = api.get_media_upload_status(result.media_id_string)
    #api.update_status(status=response, media_ids=[result.media_id_string])
    return result

def gif_post(gif_url_list, msg, response):
    """
    tweets a single random GIF
    """
    random_index = random.randint(0, len(gif_url_list) - 1)  # Randomly select an index from the gif_url_list
    try:
        gif_download(gif_url_list[random_index])
        m = modifier(msg[random_index])
        tweet(m, response)
    except Exception as e:
        print("Error occurred: ", e)
        traceback.print_exc()

def search_gif(query, response):
    """
    Searches for GIFs based on a query
    """
    words = re.findall(r'\w+', query, re.MULTILINE)
    formatted_query = '+'.join(words)
    print("Searching for GIFs based on query: ", formatted_query)
    giphy_url = "https://api.giphy.com/v1/gifs/search?api_key="+giphy_api_key+"&q="+formatted_query+"&limit=20&offset=0&rating=r&lang=en"

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

    gif_post(gif_urls, slugs, response)
    gif_urls = []
    slugs = []

if __name__ == "__main__":
    respond_to_timeline_tweets()
