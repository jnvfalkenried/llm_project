import json
import requests
import streamlit as st
import os

from page_components import add_common_page_elements, create_chat
from classes.chat import Chat

from streamlit_js_eval import streamlit_js_eval

sidebar_container = add_common_page_elements()
# page_container = st.sidebar.container()
# sidebar_container = st.sidebar.container()
st.title("StreamWise Chat")

st.divider()

if "GOOGLE_API_KEY" not in os.environ:
    google_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
    os.environ["GOOGLE_API_KEY"] = google_api_key

# Create a chat instance
to_hash = "gemini-1.5-flash"
chat = create_chat(to_hash, Chat)

# TODO: Wait till db is ready. Only then proceed to show input and stuff.
chat.get_input()
chat.display_messages()
chat.save_state()

if st.button("New Chat"):
    # Execute JavaScript to reload the page
    streamlit_js_eval(js_expressions="parent.window.location.reload()")