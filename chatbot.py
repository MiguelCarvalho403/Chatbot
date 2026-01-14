import json
import gc
import torch
import streamlit as st
from tools.open_data_search import OpenDataSearch
from tools.final_answer import FinalAnswer

from auxiliar_functions import *
# =============================================== Chatbot ===============================================================

class Chatbot:

    def __init__(self, max_steps=5, history_name="history", **kwargs):

    # ============ Models ==================
        # LLM
        self.tokenizer = kwargs.get('tokenizer')
        self.model = kwargs.get('model')
        self.model_config = read_yaml("config/model_config.yaml")
        
        # Embedding model         
        self.client = kwargs.get('client')
        self.encoder = kwargs.get('encoder')
        
    # ============ Tools ==================
        self.tool_open_data_search = OpenDataSearch(client=self.client, encoder=self.encoder)
        self.tool_final_answer = FinalAnswer()

        self.max_steps = max_steps
    # ============ System prompts ==================
        self.system_prompt = read_yaml("config/system_prompt.yaml")
        self.tools_doc = read_yaml("config/tools_doc.yaml")

    # ============ Memory ==================

        self.history_name = history_name
        self.messages = [] # Mémoria de curto prazo, reiniciada a cada query
        self.history = [] # Mémoria que perdura ao longo da sessão

    def _build_system_prompt(self):
        # Docstrings das ferramentas para o modelo entender

        identity = self.system_prompt.get('identity')
        response_format = self.system_prompt.get('response_format')
        tools_template = self.system_prompt.get('tools_template')
        examples = self.system_prompt.get('examples')

        system_prompt = identity + response_format + tools_template + str(self.tools_doc) + examples

        return system_prompt
    
    async def open_data_search(self, tool_data):
        tool_name = "open_data_search"

        observation = await self.tool_open_data_search.open_data_search(tool_data.get('parameters').get('query'))
        
        self.short_memory(role='system', tool_name=tool_name, observation=observation)
        self.history.append(self.messages)
        
        st.json(observation)

        return observation
        # Adicionar Final answer aqui, envio ao usuário é obrigátorio

    def query_catalogs(self, tool_data):
        tool_name = "query_catalogs"

        observation = self.tool_open_data_search.consult_catalogs(tool_data.get('parameters').get('dataset_id'))
        self.short_memory(role='system', tool_name=tool_name, observation=observation)
        
        return observation

    def final_answer(self, tool_data):
        tool_name = "final_answer"

        observation = self.tool_final_answer.final_answer(tool_data.get('parameters').get('response'))
        self.short_memory(role='system', tool_name=tool_name, observation=observation)
        
        self.finish()
        return observation

    def reasoning(self):
        #show_message(self.messages)
        llm_action, thinking_content = self.call_llm(self.messages) # Ação e planejamento retornado pela llm
        
        st.markdown(f"Thinking: {thinking_content}")
        st.markdown(f"Action: {llm_action}")
        st.json(f"Action: {llm_action}")

        self.short_memory(role="assistant", observation=thinking_content)
        try:
            tool_data = json.loads(llm_action.strip()) # Converte resultado da llm para json
        except json.decoder.JSONDecodeError:
            st.markdown("formato json incorreto ")
        st.json(tool_data)

        return tool_data

    def call_llm(self, messages: list) -> str:

        text = self.tokenizer.apply_chat_template( # Formata 
            messages,
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
        
        # parsing thinking content
        try:
            # rindex finding 151668 (</think>)
            index = len(output_ids) - output_ids[::-1].index(151668)
        except ValueError:
            index = 0

        thinking_content = self.tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
        content = self.tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")
        
        #print(f"thinking content: \n{thinking_content}\n")
        #print(f"ACTION: \n{content}\n")

        gc.collect()
        torch.cuda.empty_cache()

        return content, thinking_content
    
    #@measure_time
    async def chat(self, query: str) -> str:
        self.messages = [
            {'role': 'system', 'content': self._build_system_prompt()},
            {'role': 'user', 'content': query}
        ]

        step = 1
        while step < self.max_steps:
# ============================== Reasoning/Observation ==================================================
            #st.markdown(f"**STEP**{step}\n")
            step +=1

            tool_data = self.reasoning()
            
            tool_name = tool_data.get('tool_name')

# =============================== ACTION =======================================================
            if tool_name in self.tools_doc.keys():
                match tool_name:
                    case 'open_data_search':
                        observation = await self.open_data_search(tool_data)
                        return observation
                    case 'query_catalogs':
                        observation = self.query_search(tool_data)
                    case 'final_answer':
                        observation = self.final_answer(tool_data)
                        return observation

                
            st.markdown("--------------------------------------------")
# ================================================= Max steps ======================================================
        
        self.finish()
        st.markdown('Numero máximo de passos alcançado')
        return observation

    def short_memory(self, role: str, observation: any, tool_name:str|None=None) -> None:
        if role == 'system':
            self.messages.append(
                {'role': role,
                'content': f"SYSTEM OBSERVATION from tool {tool_name}: {observation}"})
        elif role == 'assistant':
            self.messages.append(
                {'role': role,
                'content': f"content: {observation}"})
        else:
            self.messages.append(
                {'role': role,
                'content': f'{tool_name}: {observation}'})
# =============================================== auxiliar functions =============================================

    def clear_history(self):
        self.history.clear()

    def clear_messages(self):
        self.messages.clear()
    
    def finish(self):
        self.clear_messages()
        self.history.append(self.messages)

    def clear_catalogs(self):
        self.open_data_search.clear_catalogs()

from auxiliar_functions import load_llm
from auxiliar_functions import load_vectorstore

async def main():
    
    model, tokenizer = load_llm("Qwen/Qwen3-0.6B")
    encoder, client = load_vectorstore()
    chatbot = Chatbot(model=model, tokenizer=tokenizer, encoder=encoder, client=client)
    
    while True:
        prompt = str(input("Diga algo> "))
        if prompt == "q":
            break
        res = await chatbot.chat(prompt)
        print(res)

    del model, tokenizer, encoder, client, chatbot

import asyncio

if __name__ == '__main__':
    asyncio.run(main())
    pass