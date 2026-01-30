import chromadb
from chromadb.utils import embedding_functions
import os

# Initialize ChromaDB Client
# PersistentClient saves data to disk
chroma_client = chromadb.PersistentClient(path="./data/chroma_db")

# Use Google Generative AI Embeddings
def get_embedding_function(api_key):
    return embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=api_key)

def get_collection(name: str, api_key: str):
    return chroma_client.get_or_create_collection(
        name=name,
        embedding_function=get_embedding_function(api_key)
    )

def add_documents(collection_name: str, documents: list, metadatas: list, ids: list, api_key: str):
    collection = get_collection(collection_name, api_key)
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

def query_documents(collection_name: str, query_text: str, n_results: int, api_key: str):
    collection = get_collection(collection_name, api_key)
    return collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
