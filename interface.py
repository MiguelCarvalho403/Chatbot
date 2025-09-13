import streamlit as st
#from llm import llm_response
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

llm_model = "Qwen/Qwen3-1.7B"

def llm_response(prompt):
    
    response = pipeline("text-generation", model=llm_model, trust_remote_code=True, device='cpu')(prompt, max_length=2048, temperature=0.1, top_p=0.7, repetition_penalty=1.1)[0]['generated_text']
    #tokenizer = AutoTokenizer.from_pretrained(llm_model, trust_remote_code=True, device='cpu')
    #model = AutoModelForCausalLM.from_pretrained(llm_model, trust_remote_code=True)
    #llm = pipeline("text-generation", model=model, tokenizer=tokenizer, max_length=2048, temperature=0, top_p=0.7, repetition_penalty=1.1)
    #response = llm(prompt)[0]['generated_text']
    return response

st.set_page_config(page_title="Open data chatbot", layout="wide")
st.title("Open data chatbot")

#Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
#prompt = st.chat_input("What is up?")
#if prompt:
# := does assignment and returns the value, so we can use it inside the if statement

if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = llm_response(prompt)  # Replace with your own function to generate a response
    # Display amodel_qwen = "Qwen/Qwen3-1.7B"model_qwen = "Qwen/Qwen3-1.7B"ssistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

#st.button("Clear Conversation", on_click=lambda: st.session_state.clear())
