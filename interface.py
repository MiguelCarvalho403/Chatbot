import streamlit as st
from chatbot import Chatbot
from auxiliar_functions import load_llm
from auxiliar_functions import load_vectorstore
import numpy as np
import time
import asyncio

async def streamlit_inter():

    if 'loaded' not in st.session_state:
        # Envolve e chama na mesma linha
        st.session_state.model, st.session_state.tokenizer = load_llm("Qwen/Qwen3-0.6B")
        st.session_state.encoder, st.session_state.client = load_vectorstore()
        st.session_state.loaded = True

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = Chatbot(model=st.session_state.model, tokenizer=st.session_state.tokenizer,
                        client=st.session_state.client, encoder=st.session_state.encoder,
                        max_steps=3)

    left, middle, right = st.columns(3)
    if left.button("Reset", width="stretch"):
        st.session_state.messages.clear()
        st.session_state.chatbot = Chatbot(model=st.session_state.model, tokenizer=st.session_state.tokenizer,
                        client=st.session_state.client, encoder=st.session_state.encoder,
                        max_steps=3)

    st.title("Chatbot dados governamentais abertos")

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):  
            st.markdown(message["content"])

    if prompt := st.chat_input("Escreva aqui"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        response = await st.session_state.chatbot.chat(prompt)

        #with st.chat_message("assistant"):
        #    st.markdown(response.get('parameters').get('response'))

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
    st.markdown("--------------------------------------------")


if __name__ == '__main__':
    asyncio.run(streamlit_inter())