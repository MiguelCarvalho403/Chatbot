import streamlit as st
import text, chatbot

def main():
    st.set_page_config(page_title="Chatbot Dados governamentais", page_icon=":robot_face:")
    #st.title("Chatbot Dados governamentais")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if 'conversation' not in st.session_state:
        st.session_state.conversation = None

    if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
    # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        response = st.session_state.conversation(prompt)  # Replace with your own function to generate a response
    # Display amodel_qwen = "Qwen/Qwen3-1.7B"model_qwen = "Qwen/Qwen3-1.7B"ssistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
    # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

    with st.sidebar:
        st.subheader("Arquivos")
        pdf_docs = st.file_uploader("carregue pdf files", accept_multiple_files=True)
    
        if st.button("Processar"):
            all_files_text = text.process_files(pdf_docs)
            
            chunks = text.create_text_chunks(all_files_text)  # Transforma arquivo em chunks
            
            vectorstore = chatbot.create_vectorstore(chunks) # Cria o vectorstore
            
            st.session_state.conversation = chatbot.create_conversation_chain(vectorstore)
        
        st.button("Clear Conversation", on_click=lambda: st.session_state.clear())

if __name__ == '__name__':

    main()

main()