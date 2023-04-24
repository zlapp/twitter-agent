from langchain.agents import create_openapi_agent
from langchain.agents.agent_toolkits import OpenAPIToolkit
from langchain.llms.openai import OpenAI
from langchain.requests import RequestsWrapper
from langchain.tools.json.tool import JsonSpec
import os
import yaml
import tweepy
import random
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain, ConversationChain
from langchain.vectorstores import DeepLake
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import VectorStoreRetrieverMemory
from twitter_actions import fetch_token

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

api = tweepy.API(auth)

refreshed_token = fetch_token()

with open("twitter_openapi.yaml") as f:
    data = yaml.load(f, Loader=yaml.FullLoader)
json_spec=JsonSpec(dict_=data, max_value_length=4000)

headers = {'Authorization': f'Bearer {auth.access_token}'}
twitter_requests_wrapper=RequestsWrapper(headers=headers)

openapi_toolkit = OpenAPIToolkit.from_llm(OpenAI(temperature=0.8), json_spec, twitter_requests_wrapper, verbose=True)
twitter_agent_executor = create_openapi_agent(
    llm=OpenAI(temperature=0),
    toolkit=openapi_toolkit,
    verbose=True
)

twitter_agent_executor.run("Make a funny tweet about Jeff Bezos.")
