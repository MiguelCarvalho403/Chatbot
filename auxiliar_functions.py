from googletrans import Translator
from transformers import AutoModelForCausalLM, AutoTokenizer
from qdrant_client import models, QdrantClient
from sentence_transformers import SentenceTransformer
import yaml
import time
import streamlit as st
from functools import wraps
#=============================================== loading models ==============================================================

def load_llm(model_name):
    
    # load the tokenizer and the model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        dtype="auto",
        device_map="auto"
    )

    return model, tokenizer


def load_vectorstore(model_name="Qwen/Qwen3-Embedding-0.6B", device='cpu'):

    encoder = SentenceTransformer(model_name, device=device)
    client = QdrantClient(path="metadados/VectorStore") # Carrega vectorstore em disco

    return encoder, client

# ========================================= Auxiliar functions ==========================================

def read_yaml(path: str)->dict:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return data

def write_yaml(path: str, data: dict, overwrite: bool=False)->None:
    if not overwrite:
        with open(path, "r") as f:
            existing_data = yaml.safe_load(f)
        if existing_data is not None:
            update_data = {**existing_data, **data}
        else:
            update_data = data
        
    with open(path, "w") as f:
        yaml.dump(update_data, f, default_flow_style=False)
        
def measure_time(func):
    @wraps
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        end = time.perf_counter()
        st.markdown(f"Execution time: {end-start}")
        return result
    return wrapper

if __name__ == "__main__":
    model, tokenizer = load_llm("Qwen/Qwen3-0.6B")
    print(model.config.name_or_path)