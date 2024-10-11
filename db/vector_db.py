from flask import Flask, request, jsonify, Response
import faiss
import numpy as np
import json
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
import os

app = Flask(__name__)

# API
if "GOOGLE_API_KEY" not in os.environ:
    print("Please set the GOOGLE_API_KEY environment variable")

# Opening JSON data file
with open('/data/movie_data.json', 'r') as file:
    movie_data = json.load(file)

# Preparing the data
page_contents = []
metadatas = []
i = 0
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
        'genres': movie['genres'],
        'rating': movie['rating']
    }
    metadatas.append(metadata)
    i += 1
    if i == 10:
        break

# Embedding model
embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Initialize the FAISS index (you may want to save/load this from a persistent store)
dimension = 768
index = faiss.IndexFlatL2(dimension)
vector_store = FAISS(embedding_model, index, InMemoryDocstore(),{})
vector_store.add_texts(page_contents, metadatas=metadatas)


@app.route('/search', methods=['POST'])
def search():
    data = request.json
    app.logger.info(f"Received data: {data}")
    results = vector_store.similarity_search(data['query'], k=10)

    results_serializable = [
        {   
            'metadata': doc.metadata,
            'content': doc.page_content
        } for doc in results
    ]

    return Response(json.dumps(results_serializable), mimetype='application/json')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
