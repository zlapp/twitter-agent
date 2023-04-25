import os
import tweepy
import pytz
from dotenv import load_dotenv
from datetime import datetime, timedelta
import requests
import twitter_actions

load_dotenv()

GIPHY_API = os.getenv("GIPHY_API", "")
url = f'https://api.giphy.com/v1/gifs/trending?api_key={GIPHY_API}'

token = twitter_actions.fetch_token()

response = requests.get(url)

if response.status_code == 200:
    trending_gifs = response.json()
    print(trending_gifs['data'][0]['url'])
    print(trending_gifs['data'][0]['title'])
else:
    print(f"Request failed with status code {response.status_code}")

gif_url = trending_gifs['data'][0]['url']
gif_id = trending_gifs['data'][0]['id']
gif_title = trending_gifs['data'][0]['title']

import requests

def upload_gif_v2_chunked(gif_url):
    response = requests.get(gif_url)
    gif_data = response.content

    # Step 1: Initialize the media upload
    init_url = "https://upload.twitter.com/1.1/media/upload.json"
    headers = {
        "Authorization": "Bearer {}".format(token["access_token"]),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    init_payload = {
        "command": "INIT",
        "total_bytes": len(gif_data),
        "media_type": "image/gif",
        "media_category": "tweet_gif",
    }
    init_response = requests.post(init_url, headers=headers, data=init_payload)

    if init_response.status_code != 201:
        print(f"Media initialization failed with status code {init_response.status_code}")
        return None

    media_id = init_response.json()["media_id_string"]

    # Step 2: Upload the GIF in chunks
    upload_url = "https://upload.twitter.com/1.1/media/upload.json"
    upload_headers = {
        "Authorization": "Bearer {}".format(token["access_token"]),
        "Content-Type": "multipart/form-data",
    }
    upload_payload = {
        "command": "APPEND",
        "media_id": media_id,
        "segment_index": 0,
    }
    upload_files = {"media": ("gif_image.gif", gif_data, "image/gif")}
    upload_response = requests.post(upload_url, headers=upload_headers, data=upload_payload, files=upload_files)

    if upload_response.status_code != 204:
        print(f"Media upload failed with status code {upload_response.status_code}")
        return None

    # Step 3: Finalize the media upload
    finalize_url = "https://upload.twitter.com/1.1/media/upload.json"
    finalize_headers = {
        "Authorization": "Bearer {}".format(token["access_token"]),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    finalize_payload = {
        "command": "FINALIZE",
        "media_id": media_id,
    }
    finalize_response = requests.post(finalize_url, headers=finalize_headers, data=finalize_payload)

    if finalize_response.status_code == 201:
        return media_id
    else:
        print(f"Media finalization failed with status code {finalize_response.status_code}")
        return None

def post_tweet(tweet_text, gif_url=None):
    print("Tweeting!")

    payload = {
        "status": tweet_text,
    }

    if gif_url:
        media_id = upload_gif_v2_chunked(gif_url)
        if media_id:
            payload["media_ids"] = [media_id]
        else:
            print("Failed to upload GIF, posting text only.")

    return requests.request(
        "POST",
        "https://api.twitter.com/1.1/statuses/update.json",
        params=payload,
        headers={
            "Authorization": "Bearer {}".format(token["access_token"]),
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

# Replace 'your_gif_url' with the actual Giphy GIF URL
post_tweet("test", gif_url)
