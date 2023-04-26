from langchain.llms.openai import OpenAI
import os
import tweepy
import re
import random
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.document_loaders import TwitterTweetLoader
from prompts import prompts
from langchain.chains import LLMChain

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ACTIVELOOP_TOKEN = os.getenv("ACTIVELOOP_TOKEN", "")

api_key = os.getenv("API_KEY", "")
api_secret_key = os.getenv("API_SECRET_KEY", "")
access_token = os.getenv("ACCESS_TOKEN", "")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET", "")

auth = tweepy.OAuth1UserHandler(
    api_key, api_secret_key, access_token, access_token_secret
)

def quote_tweet():
    api = tweepy.API(auth)

    users = prompts["users"]
    user = random.choice(users)

    loader = TwitterTweetLoader.from_secrets(
        access_token=access_token,
        access_token_secret=access_token_secret,
        consumer_key=api_key,
        consumer_secret=api_secret_key,
        twitter_users=[user],
        number_tweets=50,  # Default value is 100
    )
    documents = loader.load()

    # Fetch a tweet by ID
    tweet_text = documents[0].page_content
    tweet_id = documents[0].metadata['user_info']['status']['id']
    tweet = api.get_status(tweet_id)

    # Construct the tweet URL
    tweet_url = f"https://twitter.com/{user}/status/{tweet.id}"

    llm = OpenAI(temperature=0.9)

    prompt = PromptTemplate(
        input_variables=["input_text"],
        template="You are a tweet reply agent.  Write a reply for a tweet that says: {input_text}.  Make sure the reply is under 140 characters.  Be sassy, sarcastic, and over the top.  You want to make people cry laughing.",
    )
    quote_tweet_chain = LLMChain(llm=llm, prompt=prompt)
    text = quote_tweet_chain.run(input_text=tweet_text)

    words = re.findall(r'\w+', text, re.MULTILINE)
    formatted_text = '+'.join(words)

    # Quote it in a new status
    api.update_status(formatted_text, attachment_url=tweet_url)

if __name__ == "__main__":
    quote_tweet()
