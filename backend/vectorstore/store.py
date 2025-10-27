"""Chroma vector store management."""
import hashlib
from pathlib import Path
import chromadb
from chromadb.config import Settings
from .embeddings import FastEmbedEmbeddingFunction


def get_repo_hash(repo_url: str) -> str:
    """Generate a stable hash for a repository URL."""
    return hashlib.sha256(repo_url.encode()).hexdigest()[:16]


def get_client(persist_dir: str = ".vectordb") -> chromadb.PersistentClient:
    """
    Get or create a persistent Chroma client.
    
    Args:
        persist_dir: Directory to persist the vector database
        
    Returns:
        Chroma PersistentClient instance
    """
    Path(persist_dir).mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=persist_dir,
        settings=Settings(anonymized_telemetry=False)
    )


def get_or_create_collection(
    client: chromadb.PersistentClient,
    collection_name: str,
    embedding_function: FastEmbedEmbeddingFunction | None = None
):
    """
    Get or create a collection with the specified embedding function.
    
    Args:
        client: Chroma client
        collection_name: Name of the collection
        embedding_function: Optional custom embedding function
        
    Returns:
        Chroma Collection instance
    """
    if embedding_function is None:
        embedding_function = FastEmbedEmbeddingFunction()
    
    return client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_function,
        metadata={"hnsw:space": "cosine"}
    )


def delete_collection(client: chromadb.PersistentClient, collection_name: str):
    """Delete a collection if it exists."""
    try:
        client.delete_collection(name=collection_name)
        return True
    except Exception:
        return False
