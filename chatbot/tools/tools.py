import json
from chatbot.utils import read_yaml
from icecream import ic

from config.paths import VECTOR_STORE

def search_resources(state: dict, config:dict, query: str) -> list:
    '''
    Busca por datasets no banco de dados do governo federeal com base na query do usuário

    Args:
        query: Assunto requisitado pelo usuário

    '''
    collection_name = "Recurso_metadados"

    encoder = config['configurable']['encoder']
    client = config['configurable']['client']
    
    hits = vectorstore_search(encoder=encoder, client=client, query=query, collection_name=collection_name)
    
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

def tabular_query(query:str, source:dict):
    '''
    Responde perguntas sobre dados em formato de tabelas como CSV, XLSX, XML... e bancos de dados relacionais (SQL)
    
    Args:
        query: Pergunta do usuário sobre a tabela
    '''

    source_type = source.get('source_type')

    if source_type == 'link':
        # download file
        # load file
        pass
    elif source_type == 'path':
        # load file
        pass
    elif source_type == 'data':
        pass

        
def vectorstore_search(collection_name:str, query:str, encoder, client):
    hits = client.query_points(
        collection_name=collection_name,
        query=encoder.encode(query).tolist(),
        limit=20
    ).points

    return hits

def tool_desc_jinja():
    from transformers import AutoTokenizer
    models = ["Qwen/Qwen2.5-0.5B-Instruct", "Qwen/Qwen3-0.6B"]
    model_name = models[1]

    tools = []
    my_tools = [search_resources]
    tools_description = read_yaml(path="tools/tools_description.yaml")
    
    for tool in my_tools:
        tools.append(tools_description.get(tool.__name__))
    
    ic(tools_description)
    ic(tools)

    messages = [{'role': 'assistant', 'content': 'teste'}]
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    text = tokenizer.apply_chat_template(
        messages, 
        tools=tools, # lista de dicionarios contendo informações de cada tool, segundo padrão jinja
        tokenize=False,
        #**self.model_config[self.model.config.name_or_path]['template']
    )
    ic(text)


def teste_search_resources():
    from sentence_transformers import SentenceTransformer
    from qdrant_client import QdrantClient

    query = "Crimes Rio de janeiro"

    encoder = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B", device='cpu')
    client = QdrantClient(path=VECTOR_STORE) # Carrega vectorstore em disco

    config = {'configurable':{'encoder': encoder, 'client': client}}
    state = {}

    result = search_resources(state=state,query=query, config=config)
    ic(result)

if __name__ == '__main__':
    testes = [tool_desc_jinja, teste_search_resources]
    testes[1]()
    