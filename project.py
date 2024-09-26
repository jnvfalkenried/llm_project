# Importing
import numpy as np
import os
import getpass
import faiss
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_google_genai import ChatGoogleGenerativeAI

# API
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyCNwMElBNoM1CD6cPe_KOft4EKms575LB0"

# Defining test chunks
chunks = ["Pulp fiction is a action drama with blood and shooting, good story and highly rated.",
            "Finding nemo is a child-friendly movie set in the ocean, highly rated.",
            "Superbad is a comedy with teenagers, not child friendly, medium rating"]

# Defining LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    system_instruction="You are a mushroom expert. Only answer mushroom related questions.", 
    temperature=0,
)

# Embedding model
embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Setting FAISS dimension
index = faiss.IndexFlatL2(768)

# Creating FAISS database
vector_store = FAISS(embedding_model, index, InMemoryDocstore(),{})

# Adding embeddings to the database
vector_store.add_texts(chunks)

# Searching the database
query = "I want to watch a shooting movie"
results = vector_store.similarity_search(query, k=1)

print(results)