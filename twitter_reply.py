import os
import tweepy
import random
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain

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
llm = OpenAI(temperature=0.9)

prompt = PromptTemplate(
    input_variables=["input_text"],
    template="You are a tweet reply agent.  You are replying to a tweet that says: {input_text}.  Make sure the reply is under 140 characters.  Be sarcastic and funny.",
)
chain = LLMChain(llm=llm, prompt=prompt)


def generate_response(input_text):
    # Use the input_text to generate a response using your Language Model
    # For example, using OpenAI's GPT-3
    response = chain.run(input_text=input_text)
    return response

def follow_back_followers(min_follower_count, max_follower_count, follow_probability):
    for follower in tweepy.Cursor(api.get_followers).items():
        if (
            not follower.following
            and min_follower_count <= follower.followers_count <= max_follower_count
        ):
            if random.random() <= follow_probability:
                try:
                    print(f"Following {follower.screen_name}")
                    follower.follow()
                except tweepy.TweepError as e:
                    print(f"Error following {follower.screen_name}: {e}")
                    break


def is_relevant(tweet, keywords):
    return any(keyword.lower() in tweet.text.lower() for keyword in keywords)


# Define a function to like tweets from the timeline with a given probability
def like_timeline_tweets(
    relevant_like_probability, irrelevant_like_probability, num_tweets, keywords
):
    authenticated_user_id = api.get_user(screen_name="lil_bigsky_agi").id
    for tweet in tweepy.Cursor(api.home_timeline).items(num_tweets):
        if tweet.favorited != True and tweet.user.id != authenticated_user_id:
            like_probability = (
                relevant_like_probability
                if is_relevant(tweet, keywords)
                else irrelevant_like_probability
            )
            if random.random() <= like_probability:
                try:
                    print(f"Liking tweet from {tweet.user.screen_name}: {tweet.text}")
                    api.create_favorite(tweet.id)
                except tweepy.TweepError as e:
                    print(f"Error liking tweet from {tweet.user.screen_name}: {e}")


def retweet_timeline_tweets():
    # Retweet probability (5%)
    RETWEET_PROBABILITY = 0.05
    # Scaling factor for retweet probability of tweets from followers
    FOLLOWER_FACTOR = 2

    # Get the user's timeline
    timeline = api.home_timeline()

    # Get the list of user IDs who follow the authenticated user
    follower_ids = api.get_follower_ids()

    # Retweet random tweets with 5% probability, with higher probability for tweets from followers
    for tweet in timeline:
        if not tweet.retweeted and not tweet.favorited:
            probability = RETWEET_PROBABILITY
            if tweet.user.id in follower_ids:
                probability *= FOLLOWER_FACTOR
            if random.random() < probability:
                try:
                    api.retweet(tweet.id)
                    print(f"Retweeted: {tweet.text}")
                except tweepy.TweepError as e:
                    print(f"Error retweeting: {e}")


def should_respond():
    return random.random() <= 0.02  # 5% probability of returning True

def generate_response(tweet):
    # Generate a response using your LLM agent based on the context of the tweet
    response = chain.run(tweet.text)  # Replace this with your actual LLM-generated response
    print(f"Responding to {tweet.user.screen_name}: {tweet.text}")
    return response

def respond_to_timeline_tweets():
    timeline_tweets = api.home_timeline(count=100)  # Fetch 100 most recent tweets from your timeline
    my_screen_name = 'lil_bigsky_agi'  # Fetch your account's screen_name

    for tweet in timeline_tweets:
        if tweet.user.screen_name != my_screen_name and should_respond():
            response = generate_response(tweet)
            api.update_status('@{} {}'.format(tweet.user.screen_name, response), in_reply_to_status_id=tweet.id)


if __name__ == "__main__":
   respond_to_timeline_tweets()
   min_follower_count = 50
   max_follower_count = 5000
   follow_probability = 0.6  # Set the follow-back probability (0.8 = 80% chance)
   follow_back_followers(min_follower_count, max_follower_count, follow_probability)

   relevant_like_probability = (
       0.35  # Set the like probability for relevant tweets (0.65 = 65% chance)
   )
   irrelevant_like_probability = (
       0.15  # Set the like probability for irrelevant tweets (0.35 = 35% chance)
   )
   num_tweets = 20
   keywords = [
       "AGI",
       "Langchain",
       "BabyAgi",
       "Python",
       "Paradigm",
       "Ethereum",
       "Warriors",
       "NBA",
       "Coding",
       "Programming",
       "DeFi",
       "Eth",
       "Ethereum",
       "OpenAI",
   ]  # Set your relevant keywords here
   like_timeline_tweets(
       relevant_like_probability, irrelevant_like_probability, num_tweets, keywords
   )

   retweet_timeline_tweets()
