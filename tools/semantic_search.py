from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

def load_vectorstore(model_name="Qwen/Qwen3-Embedding-0.6B", device='cpu'):

    encoder = SentenceTransformer(model_name, device=device)
    client = QdrantClient(path="metadados/VectorStore") # Carrega vectorstore em disco

    return encoder, client

encoder, client = load_vectorstore()

def vectorstore_search(collection_name:str, query:str):
    hits = client.query_points(
        collection_name=collection_name,
        query=encoder.encode(query).tolist(),
        limit=20
    ).points

    return hits

if __name__ == "__main__":
    collection_name = "Recurso_metadados"
    query = "infecção"
    hits = vectorstore_search(query=query, collection_name=collection_name)
    print(hits)