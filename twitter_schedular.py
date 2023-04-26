import random
import schedule
import yaml
import time
from twitter_dm import reply_to_new_direct_messages
from twitter_gif_reply import respond_to_timeline_tweets
from twitter_quote_tweet import quote_tweet
from twitter_post_tweet import post_tweet
from twitter_like import like_timeline_tweets

with open("params.yaml", "r") as file:
    params = yaml.safe_load(file)

def weighted_random_choice(actions, probabilities):
    return random.choices(actions, probabilities)[0]

def perform_action():
    actions = [
        "reply_to_new_direct_messages",
        "quote_tweet",
        "post_tweet",
        "like_timeline_tweets",
        "respond_to_timeline_tweets",
    ]

    probabilities = [
        0.1,  # reply_to_new_direct_messages
        0.3,  # quote_tweet
        0.3,  # post_tweet
        0.2,  # like_timeline_tweets
        0.1   # respond_to_timeline_tweets
    ]

    # Select and perform an action based on the probabilities
    action = weighted_random_choice(actions, probabilities)
    action()


if __name__ == "__main__":
    perform_action()
