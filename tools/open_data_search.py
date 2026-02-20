from qdrant_client import models, QdrantClient
from sentence_transformers import SentenceTransformer
from googletrans import Translator

class OpenDataSearch:
    def __init__(self, **kwargs):
        self.client = kwargs.get('client')
        self.encoder = kwargs.get('encoder')

        self.catalogs = {} # Armazena todos os catalogos pesquisados durante a sessão
    
    def search_resources(self, query: str) -> list:

        hits = self.client.query_points(
            collection_name="Recurso_metadados",
            query=encoder.encode(query).tolist(),
            limit=200
        ).points
        resources = {}
        for hit in hits:
            id = hit.payload.get('id')
            if id not in resources.keys(): # garante que não há catalogos repitidos
                resources.update({
                "score:", hit.score,
                "Titulo: ",hit.payload.get('titulo'),
                "descricap: ", hit.payload.get('descricao'),
                "formato: ", hit.payload.get('formato'),
                "id: ", hit.payload.get('id'),
                "id conjunto: ", hit.payload.get('idConjuntoDados'),
                "link: ", hit.payload.get('link')
                })
        return resources

    def open_data_search(self, query: str) -> list:
        
        '''
        Busca por coleções dentro do banco de dados do governo federal brasileiro

        Args: 

            query: Assunto requisitado pelo usuário

        '''


        translator = Translator()

        task = "Você é um motor de busca, devolva dados mais relevantes com base na busca"

        query = f"Instrução: {task} Query: {query}"
        #query_en = await translator.translate(query_pt, src='pt', dest='en')

        #query = query_en.text

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
    
    def consult_catalogs(self, id: str) -> dict:
        '''
        tool_name = "consult_catalogs"
        
        '''
        return self.catalogs.get(id)


    def download_data(self):
        pass

    def clear_catalogs(self):
        self.catalogs.clear()

if __name__ == '__main__':
    model_name="Qwen/Qwen3-Embedding-0.6B"
    device='cpu'
    query="infecção hospitalares"

    #script_dir = os.path.dirname(os.path.abspath(__file__))
    #db_path = os.path.join(script_dir, "../metadados/VectorStore")

    encoder = SentenceTransformer(model_name, device=device)
    client = QdrantClient(path="metadados/VectorStore") # Carrega vectorstore em disco
    open = OpenDataSearch(encoder=encoder, device=device, model_name=model_name, client=client)
    try:
        print(open.open_data_search(query))
    except:
        print("Erro")
        del encoder, client, open

    pass