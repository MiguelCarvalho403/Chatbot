from transformers import AutoTokenizer, AutoModel, pipeline

from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain_huggingface import HuggingFacePipeline

# Deprecated
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

from transformers import AutoTokenizer, AutoModel, pipeline

qwen1p7 = "Qwen/Qwen3-1.7B"
qwenp6 = "Qwen/Qwen3-0.6B"

def create_vectorstore(chunks):
    
    model_name="Qwen/Qwen3-Embedding-0.6B"
    model_kwargs = {"device": "cpu"}

    embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs)
    vectorstore = FAISS.from_texts(texts=chunks, embedding=embeddings)
    return vectorstore

class Chatbot:
    def __init__(self, model_name, **kwargs):

        self.model = model_name
        self.kwargs = kwargs
        self.load_model()
    
    def load_model(self):

        tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        model = AutoModel.from_pretrained(qwen1p7, trust_remote_code=True, device_map="auto", torch_dtype=torch.float16) #device_map="auto", torch_dtype=torch.float16
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=400,
            do_sample=True,
            temperature=0.1,
            top_p=0.7,
            top_k=50,
            repetition_penalty=1.2,
            num_return_sequences=1
        )

        hf = HuggingFacePipeline(pipeline=pipe)
        return hf

    def create_conversation_chain(vectorstore):
        
        hf = HuggingFacePipeline.from_model_id(
        model_id=qwenp6,
        task="text-generation",

        pipeline_kwargs={"max_new_tokens": 400, "do_sample": True, "temperature": 0.1,
                        "top_p": 0.7, "top_k": 50, "repetition_penalty": 1.2, 
                        "num_return_sequences": 1}, device_map="auto") #device=0
        
        memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
        #Deprecated since version 0.3.1: Please see the migration guide at: https://python.langchain.com/docs/versions/migrating_memory/ It will not be removed until langchain==1.0.0.
        
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=hf,
            retriever=vectorstore.as_retriever(),
            memory=memory
        ) # Deprecated since version 0.1.17: Use create_history_aware_retriever together with create_retrieval_chain (see example in docstring)() instead. It will not be removed until langchain==1.0.
        return conversation_chain