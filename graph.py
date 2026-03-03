from transformers import AutoTokenizer, AutoModelForCausalLM

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.prebuilt import ToolNode # Classe que chama tools
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
# add_message é uma reduce_function, função que dita como um dado será modificado ao ser atualizado
# Nesse caso, add_message concatena messagens anteriores com novas sem reescrever dados anteriores

from langchain_core.messages import BaseMessage   # Classe pai que dá origem a todos os tipos de messagem no langchain
from langchain_core.messages import ToolMessage   # Classe que gerencia messagens/respotas das tools
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage
from langchain_core.messages import SystemMessage # Classe que gerencia messagens de sistema, ordens a LLM
from langchain_core.runnables import RunnableConfig

from typing import TypedDict, Dict
from typing import Annotated # Adiciona decrição a variaveis, variavel = Annotaded[tipo_variavel, "descrição"]
from typing import Sequence  # Cria uma sequência dado um tipo EX: Sequence[int], Sequence[str]...

from tools.tools import search_resources
from llm import LLM
from utils import read_yaml

from icecream import ic

# Herda da classe TypedDict, permite declarar tipos para classe
# Esta classe serve para gerenciar o estado atual do agente
''' Ver mais informações nas importações de cada função/classe''' 
# Esse tipo de classe não deve ser instanciada, serve como um blueprint para criação e gerenciamento de dicionarios
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages] # Troca de messagens entre chat e usuário
    gov_resources: Annotated[Sequence[ToolMessage], add_messages] # Recursos do governo
    # tipo da variavel messages: sequence[BaseMessages]
    # conteudo: add_messages

def init_state(state: AgentState, config: RunnableConfig):
    print('Inicializando...')
    models = config.get('configurable')
    config.get('configurable').update({'llm_wrapper':LLM(model=models['llm'], tokenizer=models['tokenizer'])})
    return {'messages': [],
            'gov_resources': [ToolMessage(content="", tool_call_id="init")]}

import uuid
def messages_router(func_name: str, result: BaseMessage)->dict:
    if func_name in ["search_resources"]:
        return {'gov_resources': [ToolMessage(content=result, tool_call_id=uuid.uuid4())]}

def llm_call(state: AgentState, config: RunnableConfig):
    llm = config['configueable']['llm_wrapper']
    system_message = SystemMessage(content='Você é uma assitente que responde sobre dados governamentais do governo brasileiro, responda conforme o requisitado')
    response = llm.invoke([system_message] + state['messages'] + [state['gov_resources'][-1]], tools)
    return {'messages': [response]}

def tool_call(state: AgentState):
    # Tipo AIMessage(content:str, tool_calls:dict('name': 'func_name', 'args': {}, 'id': 'id'), additional_kwargs:dict)
    ai_message = state['messages'][-1]
    '''OBS: Por enquanto utlizaremos tool_calls[0], permitindo a chamada de apenas uma tool por vez'''
    func_name = ai_message.tool_calls[0].get('name')
    func = globals()[func_name]
    args = ai_message.tool_calls[0].get('args')
    result= None
    
    if callable(func):
        result = func(**args)
        return messages_router(func_name, result)
    
    return {'messages': [SystemMessage(content="Função retornada não existe")]}

def should_continue(state: AgentState)-> AgentState:
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls: # testa se ultima mensagem foi uma chamada de ferramenta
        return 'continue'
    else:
        return 'user_input_node' 

def kill_robot(state: AgentState):

    last_message = state['messages'][1].content

    if last_message.lower() == "hasta la vista":
        return 'hasta la vista baby'
    else:
        return 'continue'

def user_input(state: AgentState)-> AgentState:
    '''Entrada do usuário'''

    user_input = interrupt("Entrada de dados usuário")
    
    return {'messages': [HumanMessage(content=user_input)]}


def chat_graph():

    graph = StateGraph(AgentState)

    graph.add_node('user_input_node', user_input)
    graph.add_node('llm_call_node', llm_call)

    #tool_node = ToolNode(tools=tools) # Objeto que executa ferramentas
    # OBS: O objeto ToolNode sempre irá guardar o retorno da ferramenta onde houver uma chamada de ferramenta
    # Nesse caso na variável messages, por isso é recomendavel criar um wrapper para desviar o conteúdo
    # da ferramenta para outra variável a fim de não sobrecarregar a llm durante a inferência

    graph.add_node('tools_node', tool_call) # Adiciona objeto que contém tools em um nó

    #graph.set_entry_point('llm_call_node')

    graph.add_node('init_state_node', init_state)

    graph.set_entry_point('init_state_node')
    #graph.add_edge(START, 'init_state_node')

    graph.add_edge('init_state_node', 'llm_call_node')

    graph.add_conditional_edges(
        source='llm_call_node', # determina a partir de qual nó haverá arestas condicionais   
        path=should_continue, # determina qual função escolherá o próximo nó
        
        path_map= # mapeia saída da função em path para qual nó seguirá (parametro opcional, entretanto a sáida de path deverá ser um nó existente)
        {
            'continue': 'tools_node',
            'user_input_node': 'user_input_node',
        }
    )

    graph.add_edge('tools_node', 'llm_call_node') # Aresta que retorna ao agente, criando uma conexão circular
    
    #graph.add_edge('user_input_node', 'llm_call_node')

    graph.add_conditional_edges(
        source='user_input_node',
        path=kill_robot,
        path_map=
        {   
            'hasta la vista baby': END,
            'continue': 'llm_call_node'
        }
    )

    checkpointer = InMemorySaver()  
    app = graph.compile(checkpointer=checkpointer)

    return app

# ============================= Carregando modelo =============================

tools = [search_resources] #, Final_answer]
#model_name = ["Qwen/Qwen3-0.6B", "Qwen/Qwen2.5-0.5B-Instruct"]
#model_name = model_name[0]

if __name__ == '__main__':
    pass