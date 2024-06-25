# Import necessary libraries

import openai
from openai import OpenAI
from openai.types.beta.assistant_stream_event import ThreadMessageDelta
from openai.types.beta.threads.text_delta_block import TextDeltaBlock
import streamlit as st
import pandas as pd
import numpy as np
import os

ASSISTANT_ID = "asst_0CweJUSaeYD0cNqzVkUZV4cY"

if "openai" not in st.session_state:
    st.session_state["openai"] = None
if st.session_state["openai"] is None:
    if openai.api_key:
        st.session_state["openai"] = openai.api_key

with st.sidebar:
    st.sidebar.title("Setup")
    st.sidebar.header("Set OpenAI API Key")
    openai_keystring = st.text_input(
        label="OpenAI API Key", key="chatbot_api_key", value=st.session_state["openai"]
    )

    if st.button("Set API Key"):
        openai.api_key = openai_keystring
        st.session_state["openai"] = openai_keystring
        st.success("API Key is set.")


client = OpenAI(api_key=openai.api_key)
assistant = client.beta.assistants.retrieve(assistant_id=ASSISTANT_ID)


# Title and subheader for the app
st.title("Team-Leader Chatbot")
st.subheader("Start chatting with your team-leader for the task")

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"


# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat chat_history from history on app rerun
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):

    if "thread_id" not in st.session_state:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

    with st.chat_message("user"):
        st.markdown(prompt)

    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    # Display user message in chat message container

    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id, role="user", content=prompt
    )

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        stream = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id, assistant_id=ASSISTANT_ID, stream=True
        )

        assistant_reply_box = st.empty()

        assistant_reply = ""

        for event in stream:
            if isinstance(event, ThreadMessageDelta):
                if isinstance(event.data.delta.content[0], TextDeltaBlock):
                    assistant_reply_box.empty()
                    assistant_reply += event.data.delta.content[0].text.value
                    assistant_reply_box.markdown(assistant_reply)

        st.session_state.chat_history.append(
            {"role": "assistant", "content": assistant_reply}
        )

        # stream = client.chat.completions.create(
        #     model=st.session_state["openai_model"],
        #     chat_history=[
        #         {"role": m["role"], "content": m["content"]}
        #         for m in st.session_state.chat_history
        #     ],
        #     stream=True,
        # )
        # response = st.write_stream(stream)
    # st.session_state.chat_history.append({"role": "assistant", "content": response})
