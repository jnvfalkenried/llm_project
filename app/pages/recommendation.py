import json
import requests
import streamlit as st
from page_components import ChatGoogleGenerativeAI

# Initialize ChatGoogleGenerativeAI (OpenAI-like client)
client = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    system_instruction="You are a movie expert. Only answer movie-related questions.",
    temperature=0,
)

# Set a default model if not already in session state
if "gemini_model" not in st.session_state:
    st.session_state["gemini_model"] = "gemini-1.5-flash"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages (if any) from session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask me about movies!"):
    # Add user message to chat history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call the movie expert LLM (ChatGoogleGenerativeAI) to get a response
    response = client.invoke(prompt)
    assistant_message = response.content  # Extract content from the response

    # Add the LLM's response to the chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant_message})

    # Display assistant response in chat
    with st.chat_message("assistant"):
        st.markdown(assistant_message)

    # Integrate with a vector database (Ensure vector DB is running)
    vector_db_url = "http://vector_db:5000/search"
    try:
        # Send the prompt to the vector database
        vector_db_response = requests.post(vector_db_url, json={"query": prompt})
        vector_db_response.raise_for_status()  # Raise an error for bad responses
        vector_db_data = vector_db_response


        # Parse and format the results from the vector database
        recommendations = []
        for movie in vector_db_data:
            title = movie['metadata']['title']
            genres = ", ".join(movie['metadata']['genres']) 
            rating = movie['metadata']['rating']
            plot = movie['content'].split("\n\nPlot: ")[1].split("\n\nReview:")[0].strip()  
            review = movie['content'].split("\n\nReview:")[1].strip()  
            
            # Create a formatted string for each movie
            recommendation = f"""
            **Title**: {title}
            **Genres**: {genres}
            **Rating**: {rating}
            **Plot**: {plot}
            **Review**: {review}
            """
            recommendations.append(recommendation)

        # Join all recommendations into a single string
        recommendations_str = "\n\n--\n\n".join(recommendations)  

        # Add the vector DB results to the chat history
        st.session_state.messages.append({"role": "assistant", "content": recommendations_str})

        # Display the recommendations in the chat interface
        with st.chat_message("assistant"):
            st.markdown(recommendations_str)

    except requests.RequestException as e:
        st.error(f"Could not connect to the vector database: {str(e)}")
