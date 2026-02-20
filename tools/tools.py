from langchain_core.tools import tool
from langchain_core.tools import render_text_description
from langchain_core.utils.function_calling import convert_to_openai_tool

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

import json
from icecream import ic

from tools.semantic_search import vectorstore_search

def a(content: str)-> str:
    '''
    Retorna Resultado ao usuários

    Args:

        content: Texto apresentando o resultado obtido
    '''

    return content

def search_resources(query: str) -> list:

    '''
    busca por datasets no banco de dados do governo federeal com base na query do usuário

    Args:

        query: Assunto requisitado pelo usuário

    '''
    collection_name = "Recurso_metadados"

    hits = vectorstore_search(query=query, collection_name=collection_name)
    
    resources = {}

    for hit in hits:
        id = hit.payload.get('id')
    
        resources.update({id: {
        "score:": hit.score,
        "Titulo: ": hit.payload.get('titulo'),
        "descricap: ": hit.payload.get('descricao'),
        "formato: ": hit.payload.get('formato'),
        "id: ": hit.payload.get('id'),
        "id conjunto: ": hit.payload.get('idConjuntoDados'),
        "link: ": hit.payload.get('link')
        }})
    return resources
    
def tool_desc_langchain():
    my_tools = [add, sub]
    ic(render_text_description(my_tools))
    print(f"Tipo do objeto: {type(add)}") 
    # <class 'langchain_core.tools.StructuredTool'>

    print(f"Nome: {add.name}")
    print(f"Argumentos (Pydantic): {add.args}")

    # Mesmo que você não use OpenAI, essa função utilitária mostra 
    # o esquema exato que o LangChain extraiu.
    schema_bruto = convert_to_openai_tool(add)
    print("\n--- O JSON QUE VAI PRO LLM ---")
    print(json.dumps(schema_bruto, indent=2))

from transformers import AutoTokenizer

def tool_desc_jinja():
    my_tools = [add, sub, get_current_temperature]
    models = ["Qwen/Qwen2.5-0.5B-Instruct", "Qwen/Qwen3-0.6B"]
    model_name = models[1]

    messages = [{'role': 'assistant', 'content': 'teste'}]
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    text = tokenizer.apply_chat_template(
        messages, 
        tools=my_tools, # lista de dicionarios contendo informações de cada tool, segundo padrão da openai
        tokenize=False,
        #**self.model_config[self.model.config.name_or_path]['template']
    )
    ic(text)

from transformers.utils import get_json_schema

def tool_desc_trans():
    tool = get_json_schema(search_resources) # Mesmo que passa pelo jinja
    ic(tool)

def teste_search_resources():
    query = "Crimes Rio de janeiro"
    result = search_resources(query)
    ic(result)

if __name__ == '__main__':
    teste_search_resources()
    pass
