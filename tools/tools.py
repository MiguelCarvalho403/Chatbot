import json
from utils import read_yaml
from icecream import ic

def search_resources(query: str) -> list:
    from semantic_search import vectorstore_search
    '''
    Busca por datasets no banco de dados do governo federeal com base na query do usuário

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

        

def tool_desc_langchain():
    from transformers import AutoTokenizer
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
    query = "Crimes Rio de janeiro"
    result = search_resources(query)
    ic(result)

if __name__ == '__main__':
    testes = [tool_desc_jinja, teste_search_resources]
    testes[0]()
    