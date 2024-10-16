# Movie Expert Chatbot with Vector Database Integration

This application is a movie recommendation and review chatbot powered by Gemini 1.5 LLM. The chatbot provides detailed responses to movie-related queries and fetches movie recommendations and reviews using an integrated Chroma vector database. It is built using Python, Streamlit, and Docker for ease of deployment and scalability.

## Key Features

- **Interactive Chat Interface**: Users can ask movie-related questions and receive responses from the Gemini 1.5 model.
- **Movie Recommendations**: The app integrates with a vector database to provide movie recommendations, metadata, and reviews.
- **Multimodality**: Users can search movies based on images.
- **Session Persistence**: Chat history is preserved during the session to allow users to refer to previous interactions.
- **Formatted Responses**: Movie titles, genres, ratings, plots, and reviews are nicely formatted for easier reading.

## Installation and Usage

### 1. Clone the Repository

```bash
git clone https://github.com/jnvfalkenried/llm_project.git
cd llm_project
```
### 2. Set up Environment Variables

Create an `.env` file and add your Gemini API Key:

```bash
echo "GOOGLE_API_KEY=<YOUR GEMINI API KEY>" > .env
```

### 3. Start the Application

```bash
docker compose up
```

### 4. Access the Application

Once the containers are running, the chatbot can be accessed in your browser at: [http://127.0.0.1:8501/](http://127.0.0.1:8501/).

## Architecture Overview

The application architecture consists of two main Docker containers:

- App Container:
    - Runs the Streamlit application.
    - Handles user interactions, generates responses via the Gemini 1.5 LLM, and fetches movie data from the vector database.
- Vector Database Container:
    - Runs a Chroma vector database that stores movie metadata and reviews.
    - Supports similarity searches to provide movie recommendations.

The application is containerized using Docker Compose for ease of management and deployment. Additional information can be found in the `docker-compose.yml` file.

## Application Structure

The main application runs inside a docker container. It is a streamlit app, that connects to the Vector DB in order to query it. The main sites of the application are:
- `about.py`: Provides general information about the app.
- `recommendtions.py`: Contains the main logic for generating movie recommendations using the vector database. This file connects to the database to query movie data. 

## Vector Database
The Chroma vector database stores metadata and reviews for a wide range of movies. The app queries the database to recommend similar movies based on user input. It supports similarity search by using vector embeddings of movie data.

- **Port**: The vector database runs internally on port `5000` and is exposed externally on port `5001` for querying.
- **Persistent Storage**: The database volume is mapped to the `./data` directory to ensure that data remains persistent even if the container is restarted.

Example API response from the vector DB:

```json
[
    {
        "metadata": {
            "title": "Inception",
            "genres": ["Sci-Fi", "Thriller"],
            "rating": "8.8",
            "type": "movie"
        },
        "content": "Title: Inception\n\nPlot: A thief who steals corporate secrets..."
    }
]
```

## Example Usage

Here is an example where the input is the image on the left as well as the text : "Could you please recommend some movies with a rating above 7 that relate to this image ?". The chatbot then returns a list of movies that satisfy the given criteria and are related to the input image.

![Screenshot of the Chatbot using an Image and a Comment as Input](archive/Example%20input.png)
