import streamlit as st
import google.generativeai as genai
from itertools import groupby
import os
import requests

def convert_messages_format(messages):
    new_messages = []
    system_prompt = None
    if len(messages) > 0 and messages[0]["role"] == "system":
        # If the first message is a system message, store it and return it.
        # Gemini requires the system prompt to be passed in separately.
        system_prompt = messages[0]["content"]
        messages = messages[1:]
    for message in messages:
        role = "model" if message["role"] == "assistant" else "user"
        new_message = {
            "role": role,
            "parts": message["content"],
        }
        new_messages.append(new_message)

    user_query = ""
    if new_messages[-1]["role"] == "user":
        user_query = new_messages.pop()
    return {"system_instruction": system_prompt, "history": new_messages, "content": user_query}

class Chat:
    function_names = []
    def __init__(self, chat_state_hash, state="empty"):

        if "chat_state_hash" not in st.session_state or chat_state_hash != st.session_state.chat_state_hash:
            # st.write("Initializing chat")
            st.session_state.chat_state_hash = chat_state_hash
            st.session_state.messages_to_display = []
            st.session_state.chat_state = state

        # Set session states as attributes for easier access
        self.messages_to_display = st.session_state.messages_to_display
        self.state = st.session_state.chat_state
    
    def clear_state(self):
        self.messages_to_display = []  # Clear the messages
    def instruction_messages(self):
        """
        Sets up the instructions to the agent. Should be overridden by subclasses.
        """
        return []

    def add_message(self, content, role="assistant", user_only=True, visible = True):
        """
        Used by app.py to start off the conversation with plots and descriptions.
        """
        message = {"role": role, "content": content}
        self.messages_to_display.append(message)

    def get_input(self):
        """
        Get input from streamlit."""
  
        if x := st.chat_input(placeholder=f"What else would you like to know?"):
            if len(x) > 500:
                st.error(f"Your message is too long ({len(x)} characters). Please keep it under 500 characters.")

            self.handle_input(x)

    def check_input_question(self, input):
        """
        Send a request to Gemini to classify if the user input is movie-related or not.
        """
        # Get the last few messages from history for context (e.g., last 3 messages)
        history = self.messages_to_display[-1:]

        # Construct the prompt using the history and the new input
        precheck_message = [
            {"role": "system", "content": "Does this query relate to movies? Respond with either 'yes' or 'no'."},
        ] + history + [{"role": "user", "content": input}]  # Add input as the last message

        # Format the messages for the model
        converted_msgs = convert_messages_format(precheck_message)

        # Initialize the Gemini model
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="You are a classifier. Answer with 'yes' or 'no' based on whether the query is related to movie recommendation only. Use previous context to inform your decision.",
            generation_config=genai.types.GenerationConfig(temperature=0)
        )

        # Start the chat and send the messages for classification
        chat = model.start_chat(history=converted_msgs["history"])
        response = chat.send_message(content=converted_msgs["content"])

        return response.text.strip().lower()  # Return 'yes' or 'no' based on classification

    def handle_input(self, input):
        """
        The main function that calls the Gemini API and processes the response.
        """

        # Get the instruction messages.
        messages = self.instruction_messages()

        # Add a copy of the user messages. This is to give the assistant some context.
        messages = messages + self.messages_to_display.copy()

        # Add user input to messages temporarily (for classification)
        messages.append({"role": "user", "content": input})

        # Remove all items in messages where content is not a string
        messages = [message for message in messages if isinstance(message["content"], str)]

        # Classify the query to check if it's movie-related
        
        precheck_response = self.check_input_question(input)
        
        if "yes" in precheck_response.lower():  # Proceed if query is movie-related
            # Get relevant information from the user input and then generate a response.
            get_relevant_info = self.get_relevant_info(input)

            # Now add the user input to the messages.
            self.messages_to_display.append({"role": "user", "content": input})

            # This is for seeing what the response from the RAG is.
            self.messages_to_display.append({"role": "system", "content": get_relevant_info})

            # Add relevant info and input to the messages.
            messages.append({"role": "user", "content": f"Here is the relevant information to answer the user's query: {get_relevant_info}\n\n```User: {input}```"})

            # Convert messages format to the required one for the Gemini API.
            converted_msgs = convert_messages_format(messages)

            # Initialize Gemini model.
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction="You are a movie expert. Only answer movie-related questions.", 
                generation_config=genai.types.GenerationConfig(
                    temperature=0,
                )
            )

            # Start the chat and send the user message.
            chat = model.start_chat(history=converted_msgs["history"])
            response = chat.send_message(content=converted_msgs["content"])

            # Extract the response from the model.
            answer = response.text
            message = {"role": "assistant", "content": answer}

            # Add the assistant's response to the messages to display.
            self.messages_to_display.append(message)

        else:
            no_movie_related_message = [
            {"role": "system", "content": "You are a movie recommendation system. Provide a detailed response to the users question. Remember to keep the conversation focused on movies and guide the user towards related topics"},
            {"role": "user", "content": input}
        ]

            # Convert messages format to the required one for the Gemini API.
            converted_no_movie_msgs = convert_messages_format(no_movie_related_message)

            # Initialize Gemini model for general responses.
            model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="You are a movie recommendation system. Respond to the user's inquiry, guiding them toward movie-related topics.",
            generation_config=genai.types.GenerationConfig(
                temperature=0,
            )
        )

            # Start the chat and send the user message.
            chat = model.start_chat(history=converted_no_movie_msgs["history"])
            response = chat.send_message(content=converted_no_movie_msgs["content"])

            # Extract the response from the model.
            answer = response.text
            message = {"role": "assistant", "content": answer}

            # Add the assistant's response to the messages to display.
            self.messages_to_display.append(message)
                
    def display_content(self,content):
        """
        Displays the content of a message in streamlit. Handles plots, strings, and StreamingMessages.
        """
        if isinstance(content, str):
            st.write(content)
        elif isinstance(content, list):
            # If the content is a list, display each item in a column.
            for item in content:
                st.write(item)
        else:
            # So we do this in case
            try: content.show()
            except: 
                try: st.write(content.get_string())
                except:
                    raise ValueError(f"Message content of type {type(content)} not supported.")

    def display_messages(self):
        """
        Displays visible messages in streamlit. Messages are grouped by role.
        If message content is a Visual, it is displayed in a st.columns((1, 2, 1))[1].
        If the message is a list of strings/Visuals of length n, they are displayed in n columns. 
        If a message is a generator, it is displayed with st.write_stream
        Special case: If there are N Visuals in one message, followed by N messages/StreamingMessages in the next, they are paired up into the same N columns.
        """
        # Group by role so user name and avatar is only displayed once

        #st.write(self.messages_to_display)

        for key, group in groupby(self.messages_to_display, lambda x: x["role"]):
            group = list(group)

            if key == "assistant":
                avatar = "images/chatbot.png"
            else:
                try:
                    avatar = st.session_state.user_info["picture"]
                except:
                    avatar = None

            message=st.chat_message(name=key, avatar=avatar) 
            with message:
                for message in group:
                    content = message["content"]
                    self.display_content(content)
                

    def save_state(self):
        """
        Saves the conversation to session state.
        """
        st.session_state.messages_to_display = self.messages_to_display
        st.session_state.chat_state = self.state

    def get_relevant_info(self, input):
        """
        Extracts relevant information from the user input.
        """
        # TODO: Make this more error proof!
        url = "http://" + os.getenv("VECTOR_DB_URL") + "/search"
        response = requests.post(url, json={"query": input})
        return response.json()
