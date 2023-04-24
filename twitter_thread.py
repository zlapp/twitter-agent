import os
import random
import twitter_actions
from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import DeepLake
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain
from langchain.llms import OpenAI
import argparse
from langchain.chat_models import ChatOpenAI

load_dotenv()

# set the OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ACTIVELOOP_TOKEN = os.getenv("ACTIVELOOP_TOKEN", "")

embeddings = OpenAIEmbeddings()

questions = [
    "What does favCountParams do?",
    "is it Likes + Bookmarks, or not clear from the code?",
    "What are the major negative modifiers that lower your linear ranking parameters?",
    "How do you get assigned to SimClusters?",
    "What is needed to migrate from one SimClusters to another SimClusters?",
    "How much do I get boosted within my cluster?",
    "How does Heavy ranker work. what are it’s main inputs?",
    "How can one influence Heavy ranker?",
    "why threads and long tweets do so well on the platform?",
    "Are thread and long tweet creators building a following that reacts to only threads?",
    "Do you need to follow different strategies to get most followers vs to get most likes and bookmarks per tweet?",
    "Content meta data and how it impacts virality (e.g. ALT in images).",
    "What are some unexpected fingerprints for spam factors?",
    "Is there any difference between company verified checkmarks and blue verified individual checkmarks?",
]
chat_history = []

db = DeepLake(
    dataset_path="./data/the-algorithm.db",
    read_only=True,
    embedding_function=embeddings,
)

retriever = db.as_retriever()
retriever.search_kwargs["distance_metric"] = "cos"
retriever.search_kwargs["fetch_k"] = 500
retriever.search_kwargs["maximal_marginal_relevance"] = True
retriever.search_kwargs["k"] = 10

# Load model
model = ChatOpenAI(temperature=0.7)
qa = ConversationalRetrievalChain.from_llm(model, retriever=retriever)


# for question in questions:
r = random.randint(0, len(questions) - 1)
result = qa({"question": questions[r], "chat_history": chat_history})
chat_history.append((questions[r], result["answer"]))
print(f"-> **Question**: {questions[r]} \n")
print(f"**Answer**: {result['answer']} \n")

# Content summary
summary_prompt = PromptTemplate(
    input_variables=["chat_history", "questions"],
    template=""" You are an agent with the task of summarizing a topic.
        You will recieve a list of {questions} and answers {chat_history}.
        Your task it to write a short essay that summarizes the topics.
        Each paragraph should consist of three complete sentences.
        Your essay should be exactly five paragraphs long.  Always use exciting language and ocasional emojis.

        The first paraghraph must contain the following text
        "🚨🤖 WARNING: #AGI Powered Twitter 🤖🚨"
        "The following content is #AI generated and may not be suitable for all audiences."
        "Please use caution when reading this content.""

        The second paragraph should be an introduction that cleary states the topic that will be covered and why it matters to the reader.
        The second, third, and fourth paragraphs should each explain one key element of the topic.
        The fifth paragraph should be a conclusion that summarizes the main points of the essay.

        Do not refer to yourself.
        The essay should be written in the present tense and should be written in the active voice.

        """,
)
review_prompt = PromptTemplate(
    input_variables=["thread"],
    template="""You are a content review and consolidation agent.  You will recieve a list of paragraphs {thread}.
    If a paragraph is longer than 140 characters, you should split it into two or more paragraphs.
    Every paragraph should end with a "/" and the paragraph number. For example, "/1".  If you split a paragraph make sure to update the paragraph number.

    Remember, the maximum length of each paragraph must be less than 140 characters(letters).
    Make sure that the paragraphs are in the correct order and that their are no repeat numbers.

    Each paragraph should have this format.  Add one empty line between paragraphs.

    "text of the paragraph /#"

    """,
)

summary_chain = LLMChain(llm=model, prompt=summary_prompt, output_key="thread")
review_chain = LLMChain(llm=model, prompt=review_prompt, output_key="review")

overall_chain = SequentialChain(
    chains=[summary_chain, review_chain],
    input_variables=["chat_history", "questions"],
    output_variables=["thread", "review"],
    verbose=True,
)

response = overall_chain({"chat_history": chat_history, "questions": questions})
response_text = response["review"]
response_array = response_text.split("\n\n")

for response in response_array:
    print(response)

twitter_actions.post_tweet_thread(response_array)
