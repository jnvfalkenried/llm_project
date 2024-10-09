import streamlit as st
from page_components import add_common_page_elements
import os
from langchain_google_genai import ChatGoogleGenerativeAI
import requests

sidebar_container = add_common_page_elements()
# page_container = st.sidebar.container()
# sidebar_container = st.sidebar.container()
st.title("Gemini-like clone")

st.divider()


if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyCNwMElBNoM1CD6cPe_KOft4EKms575LB0"

# Set OpenAI API key from Streamlit secrets
client = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    system_instruction="You are a movie expert. Only answer movie related questions.", 
    temperature=0,
)

# Set a default model
if "gemini_model" not in st.session_state:
    st.session_state["gemini_model"] = "gemini-1.5-flash"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

if "messages" in st.session_state:
    messages = st.session_state.messages
    if len(messages) > 1:
        # Get the last user message
        prompt = messages[-1]["content"]
        # Get similiar movies from vector_db
        vector_db_url = "http://vector_db:5000/search"
        response = requests.post(vector_db_url, json={"query": prompt})
        # Display the response
        with st.chat_message("assistant"):
            st.markdown(response.json())

