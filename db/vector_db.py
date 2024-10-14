from flask import Flask, request, Response
import json
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
import os
import numpy as np
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

# API
if "GOOGLE_API_KEY" not in os.environ:
    print("Please set the GOOGLE_API_KEY environment variable")

# Opening JSON data file
with open('/data/movie_data.json', 'r') as file:
    movie_data = json.load(file)

# Preparing the data
page_contents = []
metadatas = []

for movie in movie_data:
    # Title, plot and review are set as "page content"
    page_content = f"""Title: 
{movie['title']}.

Plot: 
{movie['plot']}.

Review:
{movie['review']}"""
    page_contents.append(page_content)
    
    # Store relevant metadata
    metadata = {
        'title': movie['title'],
        'genres': ', '.join(movie['genres']),
        'rating': movie['rating'],
        'type': movie['type']
    }
    metadatas.append(metadata)

# Embedding model
embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", task_type="retrieval_document")

# Creating Chroma vector store
vector_store = Chroma(embedding_function=embedding_model, persist_directory='chroma_persistence')

app.logger.info(f"Vector store doc count: {vector_store._collection.count()}")
# Check if the vector store has already been persisted
if vector_store._collection.count() == 0:
    # Adding embeddings to the vector store
    vector_store.add_texts(texts=page_contents, metadatas=metadatas)

# Set new embedding model for the vector store
vector_store._embedding_function = GoogleGenerativeAIEmbeddings(model="models/embedding-001", task_type="retrieval_query")

all_genres = [x['genres'].split(', ') for x in vector_store.get()['metadatas']]
all_genres = set([item for sublist in all_genres for item in sublist])

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    system_instruction="Please always answer in JSON format as ask in the prompt.", 
    temperature=0,
)


def get_filter(query):
    json_input_prompt = """Please take this following user query and generate a raw JSON response of this format without markdown formatting:
                {
                  "genres": "list of genres the user requests, do not generate a string here only a list, select multiple from the following genres: """ + ', '.join(all_genres) + """",
                  "rating": "a rating range that the user requests in the format of lower bound",
                  "type": "a list of type of content that the user requests, select one from the following: [movie, tvSeries]"
                }
                If no rating is given, please set it to 0.
                If no type is given, please set it to ["movie", "tvSeries"].
                User query:""" + query
    json_response = llm.invoke(json_input_prompt)
    app.logger.info(f"JSON response: {json_response.content}")
    filter_json = json.loads(json_response.content)
    user_genres = filter_json['genres']  
    regex_pattern = '|'.join(user_genres)

    filter_criteria = {
        '$and': [
            {
                'genres': {
                    '$regex': regex_pattern,
                    '$options': 'i'
                }
            },
            {
                'rating': {
                    '$in': [
                        str(round(i, 1)) for i in np.linspace(
                            int(filter_json['rating']),
                            10,
                            (10 - int(filter_json['rating'])) * 10,
                            endpoint=True
                        )
                    ]
                }
            },
            {
                'type': {
                    '$in': filter_json['type']
                }
            }
        ]
    }
    
    return filter_criteria

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    app.logger.info(f"Received data: {data}")
    filter_criteria = get_filter(data['query'])
    app.logger.info(f"Filter criteria: {filter_criteria}")
    try:
        results = vector_store.similarity_search(data['query'], k=10, filter=filter_criteria)
    except Exception as e:
        app.logger.error(f"Error: {e}")
        return Response(json.dumps([]), mimetype='application/json')
    
    results_serializable = [
        {   
            'metadata': doc.metadata,
            'content': doc.page_content
        } for doc in results
    ]
    # app.logger.info(f"Returning results: {results_serializable}")

    return Response(json.dumps(results_serializable), mimetype='application/json')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
