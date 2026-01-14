from qdrant_client import models, QdrantClient
from sentence_transformers import SentenceTransformer
from googletrans import Translator
#from registry import registry_function
import asyncio
import gc

class OpenDataSearch:
    def __init__(self, **kwargs):
        self.client = kwargs.get('client')
        self.encoder = kwargs.get('encoder')

        self.catalogs = {} # Armazena todos os catalogos pesquisados durante a sessão

    #@registry_function
    async def open_data_search(self, query: str) -> list:
        
        '''
        Name: open_data_search
        Description: Searches for datasets based on keywords.

        Arguments: 

        {
        "thought": "Brief reasoning about what to do next",
        "tool_name": "open_data_search",
        "parameters": {
            "query": "value"
            }
        }

        Return: 

            {id :
                {"score:": score,
                "id": id,
                "Titulo: ": title),
                "Nome: ": nome,
                "Descrição: ": descricao,
                }
            }
        '''


        translator = Translator()

        task = "Você é um motor de busca, devolva dados mais relevantes com base na busca"

        query_pt = f"Instrução: {task} Query: {query}"
        query_en = await translator.translate(query_pt, src='pt', dest='en')

        query = query_en.text

        hits = self.client.query_points(
            collection_name="Catalogo_metadados",
            query=self.encoder.encode(query).tolist(),
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
        self.catalogs.update(catalogs) # Atualiza catalogos

        return catalogs
    
    #@registry_function
    def consult_catalogs(self, id: str) -> dict:
        '''
        tool_name = "consult_catalogs"
        
        '''
        return self.catalogs.get(id)


    def download_data(self):
        pass

    def clear_catalogs(self):
        self.catalogs.clear()

import os

if __name__ == '__main__':
    model_name="Qwen/Qwen3-Embedding-0.6B"
    device='cpu'
    query="infecção hospitalares"
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "../metadados/VectorStore")
    
    print(f"Connecting to Qdrant at: {os.path.abspath(db_path)}")

    #encoder = SentenceTransformer(model_name, device=device)
    
    #client = QdrantClient(path=db_path) 
    
    #open_search = OpenDataSearch(encoder=encoder, client=client) # Removed unused kwargs for clarity
    
    #try:
    #    # Check if collection exists before querying to avoid the specific error
    #    if not client.collection_exists("Catalogo_metadados"):
    #        print(f"Error: Collection 'Catalogo_metadados' not found in {db_path}")
    #        print("Current collections:", [c.name for c in client.get_collections().collections])
    #    else:
    #        print(asyncio.run(open_search.open_data_search(query)))
    #        
    #except Exception as e:
    #    print(f"An error occurred: {e}")
    #    del encoder, client, open_search
    #    gc.collect()

    pass
