# Importing
import numpy as np
import json
import os
import getpass
import faiss
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
# import streamlit as st

# API
# Use the API key
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyCETYIls4JWferFGtqpsIbThTDQsF48Srk"

API_KEY = "AIzaSyCETYIls4JWferFGtqpsIbThTDQsF48Srk"

# Opening JSON data file
with open('data/movie_data.json', 'r') as file:
    movie_data = json.load(file)

# Preparing the data
page_contents = []
metadatas = []
for movie in movie_data:
    # Title, plot and review are set as "page content"
    page_content = f"Title: {movie['title']}. Plot: {movie['plot']}. Review: {movie['review']}"
    page_contents.append(page_content)
    
    # Store relevant metadata
    metadata = {
        'title': movie['title'],
        'genres': movie['genres'],
        'rating': movie['rating']
    }
    metadatas.append(metadata)

# Defining LLM
genai.configure(api_key=API_KEY)
llm = genai.GenerativeModel("gemini-1.5-flash", system_instruction="You are a movie expert. Only answer movie related questions.")

# Embedding model
embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Creating FAISS database and embedding data
index = faiss.IndexFlatL2(768)
vector_store = FAISS(embedding_model, index, InMemoryDocstore(),{})
vector_store.add_texts(page_contents, metadatas=metadatas)

image_path = "./Capture2.png"

myfile = genai.upload_file(image_path)

user_query = "I want movies over rating 5"

json_input_prompt = f"""\n\nPlease take this following attached image of myfile and generate a raw JSON response of this format without markdown formatting:
        {{
            "genres": "list of genres the user requests, do not generate a string here only a list",
            "rating": "a rating range that the user requests in the format [x,y]",
        }}
        If no rating is given, please set it to [0,10].
        User query:""" + user_query

json_response = llm.generate_content([myfile, "\n\n", json_input_prompt],generation_config=genai.types.GenerationConfig(
                    temperature=1.0,
                ))
print(json_response._result.candidates[0].content.parts[0].text)
filter_criteria = json.loads(json_response._result.candidates[0].content.parts[0].text.replace('\n', ''))
# print('image query section output: ',filter_criteria)
image_query = llm.generate_content(
    [myfile, "Capture the text from the image and translate into english and give me only main information like title?"]
)
# print('user query from image: ',image_query._result.candidates[0].content.parts[0].text.replace('\n', ' '))
image_query = image_query._result.candidates[0].content.parts[0].text.replace('\n', ' ') 
results = vector_store.similarity_search(image_query, k=10)
# print("results", results)

def filter_results(results, criteria):
    #print(criteria)
    min_rating, max_rating = criteria['rating']
    filtered_results = []
    
    for result in results:
        # Filter for only results within the rating range
        if min_rating <= float(result.metadata['rating']) <= max_rating:
            # Filter for results where genre overlaps 
            if any(genre in result.metadata['genres'] for genre in criteria['genres']):
                filtered_results.append(result)
    
    return filtered_results

filtered_movies = filter_results(results, filter_criteria)
# print("filtered movies", filtered_movies)

input_movies = []
for movie in filtered_movies:
    temp_string = str(movie.metadata) + movie.page_content
    input_movies.append(temp_string)

# print("input movies", input_movies)
input_prompt = """ Please summarize each of the movies given to you at the end of the prompt in a 
                    bullet point list as a recommendation to the user. 
                    Each entry in the list is a separate movie. 
                    Answer as if you are recommending the movies based on a request from the user. 
                    Always mention the title and rating of the movies.
                    Also briefly mention what the users said about the movie, you can find this in the "review" field.
                    If no movies are given to you below, just say that no movies fit the users request.
                    Movie list: """ + str(input_movies)

final_response = llm.generate_content([input_prompt])

print(final_response._result.candidates[0].content.parts[0].text)

