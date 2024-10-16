# Importing
import numpy as np
import json
import os
import getpass
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_google_genai import ChatGoogleGenerativeAI

# API
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyCNwMElBNoM1CD6cPe_KOft4EKms575LB0"

# Opening JSON data file
with open('data/movie_data.json', 'r') as file:
    movie_data = json.load(file)

# Preparing the data
page_contents = []
metadatas = []
for movie in movie_data[0:30]:
    # Title, plot and review are set as "page content"
    page_content = f"Title: {movie['title']}. Plot: {movie['plot']}. Review: {movie['review']}"
    page_contents.append(page_content)
    
    # Store relevant metadata
    metadata = {
        'title': movie['title'],
        'genres': ', '.join(movie['genres']),  # Convert the list to a comma-separated string
        'rating': movie['rating']
    }
    metadatas.append(metadata)

# Defining LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    system_instruction="You are a movie expert. Only answer movie related questions.", 
    temperature=0,
)

# Embedding model
embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Creating Chroma vector store
vector_store = Chroma(embedding_function=embedding_model, persist_directory='chroma_persistence')

# Check if the vector store has already been persisted
if vector_store._collection.count() == 0:
    # Adding embeddings to the vector store
    vector_store.add_texts(texts=page_contents, metadatas=metadatas)

# Creating FAISS database and embedding data
#index = faiss.IndexFlatL2(768)
#vector_store = FAISS(embedding_model, index, InMemoryDocstore(),{})
#vector_store.add_texts(page_contents, metadatas=metadatas)

# Extracting semantic metadata from user query
user_query = "I want to watch a barbie movie with a rating over 6"
json_input_prompt = """Please take this following user query and generate a raw JSON response of this format without markdown formatting:
                {
                  "genres": "list of genres the user requests, do not generate a string here only a list",
                  "rating": "a rating range that the user requests in the format [x,y]",
                }
                If no rating is given, please set it to [0,10].
                User query:""" + user_query
json_response = llm.invoke(json_input_prompt)
filter_criteria = json.loads(json_response.content)
#print(filter_criteria)

# Retrieving movies from the database
results = vector_store.similarity_search(user_query, k=10)
#for result in results:
#    print(result.metadata)

# Function to filter the retrieved movies by metadata
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

# Apply the filter
filtered_movies = filter_results(results, filter_criteria)
#for filtered_movie in filtered_movies:
#    print(filtered_movie.metadata)

# Formatting input string to LLM
input_movies = []
for movie in filtered_movies[:4]:
    temp_string = str(movie.metadata) + movie.page_content
    input_movies.append(temp_string)
input_prompt = """ Please summarize each of the movies given to you at the end of the prompt in a 
                    bullet point list as a recommendation to the user. 
                    Each entry in the list is a separate movie. 
                    Answer as if you are recommending the movies based on a request from the user. 
                    Always mention the title and rating of the movies.
                    Also briefly mention what the users said about the movie, you can find this in the "review" field.
                    If no movies are given to you below, just say that no movies fit the users request.
                    Movie list: """ + str(input_movies)

# Generating final output from LLM
final_response = llm.invoke(input_prompt)

print(final_response.content)

print(len(filtered_movies))