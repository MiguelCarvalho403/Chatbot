from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

import yaml
import re
import uuid
import json
import time

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
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print('='*50, "Tempo de execução", "="*50)
        print(f"Tempo de execução: {end-start}")
        print('='*100, "\n")
        return result
    return wrapper


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
