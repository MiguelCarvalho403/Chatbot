import streamlit as st

from langchain_core.messages import AIMessage, ToolMessage, HumanMessage, BaseMessage, SystemMessage

from langgraph.types import Command

from transformers import AutoModelForCausalLM, AutoTokenizer

import uuid
import torch
import gc
from icecream import ic
from graph import chat_graph

def role(message: BaseMessage)-> str:
    if isinstance(message, HumanMessage):
        return "user"
    else:
        return "assistant"

def show_messages(messages: list)-> None:
    
    for message in messages:
        with st.chat_message(role(message)):
            if isinstance(message, AIMessage):
                st.markdown(message.content)
            elif isinstance(message, ToolMessage):
                st.json(message.content)
            elif isinstance(message, HumanMessage):
                st.markdown(message.content)
            elif isinstance(message, SystemMessage):
                st.markdown(message.content)
            else:
                st.markdown(f"Formato invalido {type(message)}")

llm_model_name = "Qwen/Qwen3-4B-Instruct-2507"

def streamlit_inter():
    if 'models' not in st.session_state:
        st.session_state.llm_model = AutoModelForCausalLM().from_pretrained(
                                            llm_model_name,
                                            device_map="auto",
                                            dtype='auto', 
                                            trust_remote_code=True)
        st.session_state.tokenizer = AutoTokenizer().from_pretrained(llm_model_name)

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    if 'config' not in st.session_state:
        st.session_state.config = {'configurable': {
            'thread_id': uuid.uuid4(),
            'llm': st.session_state.llm_model, 
            'tokenizer': st.session_state.tokenizer
            }}

    if 'graph' not  in st.session_state:
        st.session_state.graph = chat_graph()

    if 'first_message' not in st.session_state:
        st.session_state.first_message = False 

    left, middle, right = st.columns(3)
    if left.button("Reset", width="stretch"):
        st.session_state.messages.clear()
        st.session_state.first_message = False
        st.session_state.config = {'configurable': {
            'thread_id': uuid.uuid4()
            }}
        #del st.session_state.graph
        #st.session_state.graph = chat_graph()

    if prompt:= st.chat_input("Digite Aqui!"):

        #with st.chat_message("user"): # exibe prompt no campo de usuário
        #    st.markdown(prompt)
        st.session_state.messages.append(HumanMessage(content=prompt))
        
        if st.session_state.first_message == False:
            st.session_state.first_message = True
            for chunk in st.session_state.graph.stream({'messages': [prompt]}, st.session_state.config, stream_mode='messages'):
                st.session_state.messages.append(chunk[0])
        else:
            command = Command(resume=prompt)
            for chunk in st.session_state.graph.stream(command, st.session_state.config, stream_mode="messages"):
                st.session_state.messages.append(chunk[0])

    show_messages(st.session_state.messages)


if __name__ == '__main__':
    streamlit_inter()