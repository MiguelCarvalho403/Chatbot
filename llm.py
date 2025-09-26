from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain_huggingface.llms import HuggingFacePipeline


llm_model = "Qwen/Qwen3-1.7B"

def llm_response(prompt):

    tokenizer = AutoTokenizer.from_pretrained(llm_model, trust_remote_code=True, device='cpu')
    model = AutoModelForCausalLM.from_pretrained(llm_model, trust_remote_code=True)
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_length=2048, temperature=0, top_p=0.7, repetition_penalty=1.1)
    hf = HuggingFacePipeline(pipeline=pipe)
    
    response = ''
    return response 

def teste():
    print('teste')
    