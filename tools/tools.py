from langchain_core.tools import tool
from langchain_core.tools import render_text_description
from langchain_core.utils.function_calling import convert_to_openai_tool

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

import json
from icecream import ic
'''
Decorator @tool: Transforma funções em objetos da classe StructuredTool, assim podendo ser lidos pelo método bind_tools, informando argumentos de entrada e a saída da função,
descrição da função(DocString) informada no ato de criação da função.
'''

def load_vectorstore(model_name="Qwen/Qwen3-Embedding-0.6B", device='cpu'):

    encoder = SentenceTransformer(model_name, device=device)
    client = QdrantClient(path="metadados/VectorStore") # Carrega vectorstore em disco

    return encoder, client

encoder, client = load_vectorstore()

#@tool
def add(a: float, b:float) -> float:
    '''
    Realiza a soma de dois números
    
    Args:
        a: primeiro operando
        b: Segundo operando
    
    '''
    return a+b

#@tool
def sub(a: float, b:float) -> float:
    '''
    Realiza a subtração de dois números
    
    Args:
        a: primeiro operando
        b: Segundo operando
    '''
    
    return a-b

def get_current_temperature(location: str, unit: str):
    """
    Get the current temperature at a location.

    Args:
        location: The location to get the temperature for, in the format "City, Country"
        unit: The unit to return the temperature in. (choices: ["celsius", "fahrenheit"])
    """
    return 22.

def Final_answer(content: str)-> str:
    '''
    Retorna Resultado ao usuários

    Args:

        content: Texto apresentando o resultado obtido
    '''

    return content

def catalog_search(query: str) -> list:    
    '''
    Busca por catalogos no banco de dados abertos do governo federal brasileiro

    Args:

        query: Requisição do usuário por dados
    '''

    task = "Você é um motor de busca, devolva dados mais relevantes com base na busca"

    query = f"Instrução: {task} Query: {query}"
    #query_en = await translator.translate(query_pt, src='pt', dest='en')

    #query = query_en.text

    hits = client.query_points(
        collection_name="Catalogo_metadados",
        query=encoder.encode(query).tolist(),
        limit=5,
    ).points

    catalogs = {} # catalogo temporario retornado, respectivo a cada query individual

    for hit in hits:
        id = hit.payload.get('id')
        if id not in catalogs.keys(): # garante que não há catalogos repitidos
            catalogs.update({ id :
                {"score:": hit.score,
                "id": id,
                "Titulo: ": hit.payload.get('title'),
                "Nome: ": hit.payload.get('nome'),
                "Descrição: ": hit.payload.get('descricao'),
                #"Nome organização": hit.payload.get('nomeOrganizacao'),
                #"catalogacao": hit.payload.get('catalogacao'),
                #"ultimaAtualizacaoDados'": hit.payload.get('ultimaAtualizacaoDados'), 
                }
            })
    catalogs.update(catalogs) # Atualiza catalogos

    return catalogs

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
    tool = get_json_schema(catalog_search) # Mesmo que passa pelo jinja
    ic(tool)

if __name__ == '__main__':
    tool_desc_trans()
    pass
