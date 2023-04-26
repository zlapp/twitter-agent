import random
import schedule
import time
from twitter_dm import reply_to_new_direct_messages
from twitter_gif_reply import respond_to_timeline_tweets
from twitter_quote_tweet import quote_tweet
from twitter_post_tweet import post_tweet
from twitter_like import like_timeline_tweets


def weighted_random_choice(actions, probabilities):
    return random.choices(actions, probabilities)[0]

def perform_action():
    actions = [
        reply_to_new_direct_messages,
        quote_tweet,
        post_tweet,
        like_timeline_tweets,
        respond_to_timeline_tweets
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


def job():
    perform_action()

# Schedule the job to run every 20 minutes
schedule.every(20).minutes.do(job)

# Keep the script running indefinitely and execute scheduled jobs
while True:
    schedule.run_pending()
    time.sleep(1)
