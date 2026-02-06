from transformers import AutoTokenizer, AutoModelForCausalLM

from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from langchain_core.messages import ToolMessage
from langchain_core.messages import AIMessage

import torch
import gc
import json
import time
import yaml
import re
import uuid

from icecream import ic

def measure_time(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print('='*50, "Tempo de execução", "="*50)
        print(f"Tempo de execução: {end-start}")
        print('='*100, "\n")
        return result
    return wrapper

def read_yaml(path: str)->dict:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return data

def langchain_to_jinja(messages: list) -> list:
    jinja_messages = []
    for message in messages:
        if isinstance(message, SystemMessage):
            jinja_messages.append({'role': 'system', 'content': message.content})

        elif isinstance(message, HumanMessage):
            jinja_messages.append({'role': 'user', 'content': message.content})

        elif isinstance(message, ToolMessage):
            jinja_messages.append({'role': 'tool', 'content': message.content})

        elif isinstance(message, AIMessage):
            jinja_messages.append({'role': 'assistant', 'content': message.content})

    return jinja_messages

def jinja_to_langchain(ai_message: str, think: str) -> AIMessage:
    tool_pattern = r"<tool_call>.*?</tool_call>"   

    try: # Se a resposta for um tool, o objeto AIMessage as receberá
    
        tools = re.findall(tool_pattern, ai_message, flags=re.DOTALL) # extrai tools de ai_message, retorna lista de str
        tool_calls = []

        for tool in tools:
            tool_str = re.sub(r"</?tool_call>", "", tool).strip() # retira tags
            tool_json = json.loads(tool_str)
            
            #formato requisitado pelo langgraph e objeto AIMessage para reconhecer tools
            tool_calls.append({
                'name': tool_json['name'],
                'args': tool_json['arguments'],
                'id': f"call_{uuid.uuid4().hex[:8]}"
            })
        ai_message = AIMessage(content=ai_message, 
                               tool_calls=tool_calls, 
                               additional_kwargs={"thinking": think})
        
        return ai_message
    
    except json.JSONDecodeError: # Caso a resposta não seja uma chamada de ferramenta
        raise Exception("Não é um JSON válido")


class LLM():

    def __init__(self, max_steps=5, history_name="history", **kwargs):

    # ============ Models ==================
        # LLM
        self.model_config = read_yaml("config/model_config.yaml")

        self.tokenizer = kwargs.get('tokenizer')
        self.model = kwargs.get('model')
        
        # Embedding model         
        #self.client = kwargs.get('client')
        #self.encoder = kwargs.get('encoder')

    # ============ System prompts ==================
        #self.system_prompt = read_yaml("config/system_prompt.yaml")
        #self.tools_doc = read_yaml("config/tools_doc.yaml")
    
    @measure_time
    def call(self, messages: list, tools: list=[]) -> tuple:

            text = self.tokenizer.apply_chat_template(
                messages, 
                tools=tools, # lista de dicionarios contendo informações de cada tool, segundo padrão da openai
                tokenize=False,
                **self.model_config[self.model.config.name_or_path]['template']
            )

            #print(text)
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

            # conduct text completion
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **model_inputs,
                    **self.model_config[self.model.config.name_or_path]['generate']
                )
            output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist() 
            
            try:
                # rindex finding 151668 (</think>)
                index = len(output_ids) - output_ids[::-1].index(151668)
            except ValueError:
                index = 0

            thinking_content = self.tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
            content = self.tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

            gc.collect()
            torch.cuda.empty_cache()

            return content, thinking_content
    
    def invoke(self, messages: list, tools: list=[]) -> tuple:
        jinja_messages = langchain_to_jinja(messages)
        ai_message, think = self.call(messages=jinja_messages, tools=tools)
        langchain_message =jinja_to_langchain(ai_message, think)

        return langchain_message


from tools.tools import add, sub

def teste_call():

    tools = [add, sub]

    models = ["Qwen/Qwen2.5-0.5B-Instruct", "Qwen/Qwen3-0.6B"]
    model_name = models[1]

    messages = []

    system_prompt = {'role': 'system', 
                     'content': 
                     'Voce é um chatbot prestativo que deve responder SOMENTE com as seguintes tools: '}

    user = {'role': 'user', 'content': '2+2?'}

    messages.append(system_prompt)
    messages.append(user)

    tokenizer = AutoTokenizer.from_pretrained(model_name, device_map='auto')
    model = AutoModelForCausalLM.from_pretrained(model_name)

    llm = LLM(model=model, tokenizer=tokenizer)

    content, thinking = llm.call(messages=messages, tools=tools)

    ic(content)
    ic(thinking)

def teste_invoke():

    tools = [add, sub]
    models = ["Qwen/Qwen2.5-0.5B-Instruct", "Qwen/Qwen3-0.6B"]
    model_name = models[1]

    model = AutoModelForCausalLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    llm = LLM(model=model, tokenizer=tokenizer)

    messages = [SystemMessage(content='Você é uma assitente que realiza operações matematicas, responda conforme o requisitado'),
                HumanMessage(content='se 2+2=x então quanto é x+5?')]

    ai_message = llm.invoke(messages=messages, tools=tools)

    ic(ai_message)

def teste_parser():
    ai_message = '''<tool_call>
                {"name": "add", "arguments": {"a": 2, "b": 2}}
                </tool_call>'''
    tool = tool_parser(ai_message)
    ic(tool)

def teste_lj():
    pass

if __name__ == '__main__':
    testes = [teste_call, teste_invoke, teste_parser, teste_lj]
    testes[1]()