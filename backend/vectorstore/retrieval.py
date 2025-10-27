"""Retrieve relevant context from vector store."""
from typing import List, Dict, Any
from .store import get_client, get_or_create_collection, get_repo_hash


def retrieve_context(
    query: str,
    repo_url: str,
    k: int = 15,
    persist_dir: str = ".vectordb",
    collection_name: str | None = None,
    max_context_chars: int = 12000
) -> str:
    """
    Retrieve relevant context from vector store for a query.
    
    Args:
        query: Search query
        repo_url: Repository URL to determine collection
        k: Number of top results to retrieve
        persist_dir: Directory where vector database is persisted
        collection_name: Optional custom collection name
        max_context_chars: Maximum characters in assembled context
        
    Returns:
        Assembled context string
    """
    # Generate collection name from repo URL if not provided
    if collection_name is None:
        repo_hash = get_repo_hash(repo_url)
        collection_name = f"repo_{repo_hash}"
    
    # Get client and collection
    client = get_client(persist_dir)
    
    try:
        collection = get_or_create_collection(client, collection_name)
    except Exception as e:
        return f"Error: Collection '{collection_name}' not found. Please index the repository first.\n{str(e)}"
    
    # Query the collection
    results = collection.query(
        query_texts=[query],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
    
    if not results["documents"] or not results["documents"][0]:
        return "No relevant context found in the repository."
    
    # Assemble context from results
    context_parts = []
    total_chars = 0
    
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
    
    for doc, metadata, distance in zip(documents, metadatas, distances):
        # Check if we've exceeded the context limit
        if total_chars + len(doc) > max_context_chars:
            break
        
        # Format based on type
        doc_type = metadata.get("type", "unknown")
        
        if doc_type == "doc":
            path = metadata.get("path", "unknown")
            header = f"[Documentation: {path}]"
        elif doc_type == "commit":
            sha = metadata.get("sha", "unknown")[:8]
            message = metadata.get("message", "")
            header = f"[Commit {sha}: {message}]"
        else:
            header = f"[{doc_type}]"
        
        context_parts.append(f"{header}\n{doc}\n")
        total_chars += len(doc) + len(header) + 2
    
    if not context_parts:
        return "No relevant context found within size limits."
    
    context = "\n---\n\n".join(context_parts)
    return context


def search_repo(
    query: str,
    repo_url: str,
    k: int = 10,
    persist_dir: str = ".vectordb",
    collection_name: str | None = None
) -> List[Dict[str, Any]]:
    """
    Search repository and return raw results for debugging.
    
    Args:
        query: Search query
        repo_url: Repository URL
        k: Number of results
        persist_dir: Vector database directory
        collection_name: Optional custom collection name
        
    Returns:
        List of result dicts with document, metadata, and distance
    """
    if collection_name is None:
        repo_hash = get_repo_hash(repo_url)
        collection_name = f"repo_{repo_hash}"
    
    client = get_client(persist_dir)
    
    try:
        collection = get_or_create_collection(client, collection_name)
    except Exception as e:
        return [{"error": str(e)}]
    
    results = collection.query(
        query_texts=[query],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
    
    if not results["documents"] or not results["documents"][0]:
        return []
    
    formatted_results = []
    for doc, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        formatted_results.append({
            "document": doc,
            "metadata": metadata,
            "distance": distance
        })
    
    return formatted_results
