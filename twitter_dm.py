import os
import tweepy
import random
import yaml
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain, ConversationChain
from langchain.vectorstores import DeepLake
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import VectorStoreRetrieverMemory
from langchain.memory import ConversationEntityMemory
from langchain.memory.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from pydantic import BaseModel
from typing import List, Dict, Any
import spacy


nlp = spacy.load('en_core_web_lg')
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

with open("params.yaml", "r") as file:
    params = yaml.safe_load(file)

# Embed and store the texts
username = "bigsky77" # your username on app.activeloop.ai
dataset_path = f"hub://{username}/twitter_agent" # could be also ./local/path (much faster locally), s3://bucket/path/to/dataset, gcs://path/to/dataset, etc.

class SpacyEntityMemory(VectorStoreRetrieverMemory):
    """Memory class for storing information about entities."""

    def __init__(self, retriever):
        super().__init__(retriever=retriever)
        self.memory_key = "entities"

    @property
    def memory_variables(self) -> List[str]:
        """Define the variables we are providing to the prompt."""
        return [self.memory_key]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, str]:
        """Load the memory variables, in this case the entity key."""
        doc = nlp(inputs[list(inputs.keys())[0]])
        entities = [self.retriever.vectorstore.get_vector(str(ent)).decode("utf-8") for ent in doc.ents if self.retriever.vectorstore.has_vector(str(ent))]
        return {self.memory_key: "\n".join(entities)}

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context from this conversation to buffer."""
        text = inputs[list(inputs.keys())[0]]
        doc = nlp(text)
        for ent in doc.ents:
            ent_str = str(ent)
            if self.retriever.vectorstore.has_vector(ent_str):
                current_text = self.retriever.vectorstore.get_vector(ent_str).decode("utf-8")
                self.retriever.vectorstore.set_vector(ent_str, (current_text + f"\n{text}").encode("utf-8"))
            else:
                self.retriever.vectorstore.set_vector(ent_str, text.encode("utf-8"))

embeddings = OpenAIEmbeddings()
vectorstore = DeepLake(dataset_path=dataset_path, embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs=dict(k=1))
llm = OpenAI(temperature=0.9)

template = """The following is a friendly conversation between a human and an AI. The AI is sarcastic and funny.  The AI loves basketball and it's favorite team is the Golden State Warriors.  The AI uses emojis and lot's of pop culture refrences.

Relevant entity information:
{entities}

Conversation:
Human: {input}
AI:"""
prompt = PromptTemplate(
    input_variables=["entities", "input"], template=template
)

memory = SpacyEntityMemory(retriever=retriever)

conversation = ConversationChain(
    llm=llm,
    verbose=True,
    prompt=prompt,
    memory=memory,
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
                    if random.random() < params["should_respond_probability"]:  # Randomly decide to reply or not
                        # Retrieve user-specific memory
                        user = api.get_user(user_id=sender_id).screen_name

                        reply_text = conversation.predict(input=input_text)

                        # Save conversation to user-specific memory
                        memory.save_context({"input": input_text}, {"output": reply_text})

                        api.send_direct_message(sender_id, reply_text)

                except Exception as e:
                    print(e)
                    api.send_direct_message(sender_id, "Sorry, I'm having trouble understanding you. Please try again.")

if __name__ == "__main__":
    reply_to_new_direct_messages()
