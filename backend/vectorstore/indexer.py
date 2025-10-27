"""Index repository data into Chroma vector store."""
from typing import Dict, Any, List
from .store import get_client, get_or_create_collection, get_repo_hash
from .chunker import chunk_documentation, chunk_commits


def index_repo(
    repo_data: Dict[str, Any],
    repo_url: str,
    persist_dir: str = ".vectordb",
    collection_name: str | None = None
) -> str:
    """
    Index repository data into vector store.
    
    Args:
        repo_data: Output from get_repo() with commits and documentation
        repo_url: Repository URL for generating collection name
        persist_dir: Directory to persist vector database
        collection_name: Optional custom collection name
        
    Returns:
        Collection name used
    """
    # Generate collection name from repo URL if not provided
    if collection_name is None:
        repo_hash = get_repo_hash(repo_url)
        collection_name = f"repo_{repo_hash}"
    
    # Get client and collection
    client = get_client(persist_dir)
    collection = get_or_create_collection(client, collection_name)
    
    # Chunk documentation
    doc_chunks = chunk_documentation(repo_data.get("documentation", []))
    
    # Chunk commits
    commit_chunks = chunk_commits(repo_data.get("commits", []))
    
    # Combine all chunks
    all_chunks = doc_chunks + commit_chunks
    
    if not all_chunks:
        print(f"Warning: No chunks to index for {repo_url}")
        return collection_name
    
    # Prepare data for Chroma
    ids = [chunk["id"] for chunk in all_chunks]
    documents = [chunk["text"] for chunk in all_chunks]
    metadatas = [chunk["metadata"] for chunk in all_chunks]
    
    # Add to collection (Chroma will handle embeddings via the embedding function)
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    
    print(f"Indexed {len(all_chunks)} chunks ({len(doc_chunks)} docs, {len(commit_chunks)} commits) into collection '{collection_name}'")
    
    return collection_name


def get_collection_stats(collection_name: str, persist_dir: str = ".vectordb") -> Dict[str, Any]:
    """Get statistics about a collection."""
    client = get_client(persist_dir)
    try:
        collection = client.get_collection(name=collection_name)
        count = collection.count()
        
        # Get sample to check types
        sample = collection.get(limit=min(10, count), include=["metadatas"])
        
        doc_count = sum(1 for m in sample["metadatas"] if m.get("type") == "doc")
        commit_count = sum(1 for m in sample["metadatas"] if m.get("type") == "commit")
        
        return {
            "collection_name": collection_name,
            "total_chunks": count,
            "sample_doc_chunks": doc_count,
            "sample_commit_chunks": commit_count
        }
    except Exception as e:
        return {"error": str(e)}
