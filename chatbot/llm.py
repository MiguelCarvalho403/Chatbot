from transformers import AutoTokenizer, AutoModelForCausalLM

from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from langchain_core.messages import ToolMessage
from langchain_core.messages import AIMessage

import torch
import gc

from chatbot.utils import measure_time, read_yaml, jinja_to_langchain, langchain_to_jinja
from config.paths import MODEL_CONFIG

from icecream import ic

#model_name = ["Qwen/Qwen3-0.6B", "Qwen/Qwen2.5-0.5B-Instruct"]
#model_name = model_name[0]

class LLM():
 
    def __init__(self, model, tokenizer, **kwargs):

    # ============ Models ==================
        # LLM
        self.model_config = read_yaml(MODEL_CONFIG)

        self.model = model
        self.tokenizer = tokenizer

        #self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        #self.model = AutoModelForCausalLM.from_pretrained(model_name,
        #                                    device_map="auto",
        #                                     dtype=torch.float16)
        
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


#from tools.tools import add, sub

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
    def add(a: float, b:float)-> float:
        '''
        Soma dois numeros
        
        Args:
            a: Primeiro operando
            b: Segundo operando
        '''

    tools = [add]
    
    models = ["Qwen/Qwen2.5-0.5B-Instruct", "Qwen/Qwen3-0.6B"]
    model_name = models[1]

    llm = LLM()

    messages = [SystemMessage(content='Você é uma assitente que realiza operações matematicas, responda conforme o requisitado'),
                HumanMessage(content='quanto é 2 + 2')]

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

import torch

if __name__ == '__main__':
    #testes = [teste_call, teste_invoke, teste_parser, teste_lj]
    #testes[1]()
    pass