# Movie Expert Chatbot with Vector Database Integration

This application is a movie recommendation and review chatbot powered by Gemini 1.5 LLM. The chatbot provides detailed answers to movie-related queries and can also fetch movie recommendations and reviews from an integrated vector database. The app is built using Python, Streamlit, and a vector database for enhanced recommendations.

The application is built using docker, having two different containers, one for the application itself and one for runnign the Chroma database


## Usage
```
git clone https://github.com/jnvfalkenried/llm_project.git
cd llm_project
docker compose up
```

## Features

- **Interactive Chat Interface**: Users can ask movie-related questions and receive responses from the Gemini 1.5 model.
- **Movie Recommendations**: The app integrates with a vector database to provide movie recommendations, metadata, and reviews.
- **Session Persistence**: Chat history is preserved during the session to allow users to refer to previous interactions.
- **Formatted Responses**: Movie titles, genres, ratings, plots, and reviews are nicely formatted for easier reading.

## Application
The main application runs inside a docker container. It is a streamlit app, that connects to the Vector DB in order to query it. Application is compromised from two files, `about.py` and `recommendtions.py`. The important file is the `recommendations` one. 

## Vector Database
The vector database runs inside a docker container. The application can connect to the vector database (default port 5000) to provide movie recommendations.

Example API response from the vector DB 


```json
[
    {
        "metadata": {
            "title": "Inception",
            "genres": ["Sci-Fi", "Thriller"],
            "rating": "8.8"
        },
        "content": "Title: Inception\n\nPlot: A thief who steals corporate secrets..."
    }
]
```

