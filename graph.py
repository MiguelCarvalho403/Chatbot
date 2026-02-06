from transformers import AutoTokenizer, AutoModelForCausalLM

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.prebuilt import ToolNode # Classe que contem tools
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
# add_message é uma reduce_function, função que dita como um dado será modificado ao ser atualizado
# Nesse caso, add_message concatena messagens anteriores com novas sem reescrever dados anteriores

from langchain_core.messages import BaseMessage   # Classe pai que dá origem a todos os tipos de messagem no langchain
from langchain_core.messages import ToolMessage   # Classe que gerencia messagens/respotas das tools
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage
from langchain_core.messages import SystemMessage # Classe que gerencia messagens de sistema, ordens a LLM

from typing import TypedDict, Dict
from typing import Annotated # Adiciona decrição a variaveis, variavel = Annotaded[tipo_variavel, "descrição"]
from typing import Sequence  # Cria uma sequência dado um tipo EX: Sequence[int], Sequence[str]...

from tools.tools import catalog_search, add
from llm import LLM
from utils import read_yaml

import json
import uuid
import torch
import re
import gc

from icecream import ic

# Herda da classe TypedDict, permite declarar tipos para classe
# Esta classe serve para gerenciar o estdo atual do agente
''' Ver mais informações nas importações de cada função/classe''' 
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages] 
    # tipo da variavel messages: sequence[BaseMessages]
    # conteudo: add_messages
def llm_call(state: AgentState):
    system_message = SystemMessage(content='Você é uma assitente que responde sobre dados governamentais do governo brasileiro, responda conforme o requisitado')
    response = llm.invoke([system_message] + state['messages'], tools)
    return {'messages': [response]}

def should_continue(state: AgentState)-> AgentState:

    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls: # testa se ultima mensagem foi uma chamada de ferramenta
        return 'continue'
    else:
        return 'user_input_node' 

def user_input(state: AgentState)-> AgentState:
    '''Entrada do usuário'''

    user_input = interrupt("Entrada de dados usuário")
    
    return {'messages': [HumanMessage(content=user_input)]}

def chat_graph():

    graph = StateGraph(AgentState)

    graph.add_node('user_input_node', user_input)
    graph.add_node('llm_call_node', llm_call)

    tool_node = ToolNode(tools=tools) # Objeto que contém tools diponiveis
    graph.add_node('tools_node', tool_node) # Adiciona objeto que contém tools em um nó

    graph.set_entry_point('llm_call_node')

    graph.add_conditional_edges(
        source='llm_call_node', # determina a partir de qual nó haverá arestas condicionais   
        path=should_continue, # determina qual função escolherá o próximo nó
        
        path_map= # mapeia saída da função em path para qual nó seguirá (parametro opcional, entretanto a sáida de path deverá ser um nó existente)
        {
            'continue': 'tools_node',
            'user_input_node': 'user_input_node',
        }
    )
    '''Adicionar conditional edge, se ultima tool for final answer devolver resposta ao usuário'''
    graph.add_edge('tools_node', 'llm_call_node') # Aresta que retorna ao agente, criando uma conexão circular
    graph.add_edge('user_input_node', 'llm_call_node')

    checkpointer = InMemorySaver()  
    app = graph.compile(checkpointer=checkpointer)

    return app

# ============================= Carregando modelo =============================

tools = [catalog_search] #, Final_answer]
model_name = ["Qwen/Qwen3-0.6B", "Qwen/Qwen2.5-0.5B-Instruct"]
model_name = model_name[0]

model = AutoModelForCausalLM.from_pretrained(model_name,
                                             device_map="auto",
                                             dtype=torch.float16 )

tokenizer = AutoTokenizer.from_pretrained(model_name)

llm = LLM(tokenizer=tokenizer, model=model)

if __name__ == '__main__':

    pass