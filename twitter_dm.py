import os
import tweepy
import random
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain, ConversationChain
from langchain.vectorstores import DeepLake
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import VectorStoreRetrieverMemory

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


# Embed and store the texts
username = "bigsky77" # your username on app.activeloop.ai
dataset_path = f"hub://{username}/twitter_agent" # could be also ./local/path (much faster locally), s3://bucket/path/to/dataset, gcs://path/to/dataset, etc.

embeddings = OpenAIEmbeddings()
vectorstore = DeepLake(dataset_path=dataset_path, embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs=dict(k=1))
memory = VectorStoreRetrieverMemory(retriever=retriever)

llm = OpenAI(temperature=0.9)
_DEFAULT_TEMPLATE = """The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know.

Relevant pieces of previous conversation:
{history}

(You do not need to use these pieces of information if not relevant)

Current conversation:
Human: {input}
AI:"""
PROMPT = PromptTemplate(
    input_variables=["history", "input"], template=_DEFAULT_TEMPLATE
)
conversation_with_summary = ConversationChain(
    llm=llm,
    prompt=PROMPT,
    memory=memory,
    verbose=False,
)

def get_last_dm_sent_to(user_id):
    sent_dms = api.get_direct_messages()
    for dm in sent_dms:
        if dm.message_create["target"]["recipient_id"] == user_id:
            return dm
    return None

def reply_to_new_direct_messages():
    received_dms = api.get_direct_messages(count=10)
    for dm in received_dms:
        sender_id = dm.message_create["sender_id"]
        if sender_id != api.get_user(screen_name="lil_bigsky_agi").id:  # Make sure it's not a message sent by yourself
            last_dm_sent = get_last_dm_sent_to(sender_id)
            if not last_dm_sent or last_dm_sent.id < dm.id:
                try:
                    print(f"Replying to DM from {sender_id}")
                    input_text = dm.message_create["message_data"]["text"]
                    if random.random() < 0.8:  # Randomly decide to reply or not
                        # Retrieve user-specific memory
                        user = api.get_user(user_id=sender_id).screen_name

                        reply_text = conversation_with_summary.run(input=input_text)

                        # Save conversation to user-specific memory
                        memory.save_context({"input": input_text}, {"output": reply_text})

                        api.send_direct_message(sender_id, reply_text)
                except tweepy.TweepError as e:
                    print(f"Error replying to DM from {sender_id}: {e}")

if __name__ == "__main__":
    reply_to_new_direct_messages()
