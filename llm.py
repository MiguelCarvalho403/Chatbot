from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

llm_model = "Qwen/Qwen3-1.7B"

def llm_response(prompt):
    tokenizer = AutoTokenizer.from_pretrained(llm_model, trust_remote_code=True, device='cpu')
    model = AutoModelForCausalLM.from_pretrained(llm_model, trust_remote_code=True)
    llm = pipeline("text-generation", model=model, tokenizer=tokenizer, max_length=2048, temperature=0, top_p=0.7, repetition_penalty=1.1)
    response = llm(prompt)[0]['generated_text']
    return response 

def teste():
    print('teste')