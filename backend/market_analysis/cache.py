"""Market analysis caching system using ChromaDB."""
import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from chromadb import Client
from chromadb.config import Settings


def get_cache_key(project_description: str, tech_stack: str, target_audience: str) -> str:
    """
    Generate a unique cache key for market analysis parameters.
    
    Args:
        project_description: Project description
        tech_stack: Technology stack
        target_audience: Target audience
        
    Returns:
        MD5 hash as cache key
    """
    combined = f"{project_description}|{tech_stack}|{target_audience}"
    return hashlib.md5(combined.encode()).hexdigest()


def init_market_cache(persist_dir: str = ".vectordb") -> Client:
    """
    Initialize the market analysis cache collection.
    
    Args:
        persist_dir: Directory for persistent storage
        
    Returns:
        ChromaDB client
    """
    client = Client(Settings(
        persist_directory=persist_dir,
        anonymized_telemetry=False
    ))
    
    # Get or create market_analysis collection
    try:
        collection = client.get_collection(name="market_analysis_cache")
    except Exception:
        collection = client.create_collection(
            name="market_analysis_cache",
            metadata={"description": "Cached market analysis results"}
        )
    
    return client


def cache_market_analysis(
    project_description: str,
    tech_stack: str,
    target_audience: str,
    market_data: Dict[str, Any],
    persist_dir: str = ".vectordb",
    ttl_days: int = 7
) -> None:
    """
    Cache market analysis results.
    
    Args:
        project_description: Project description
        tech_stack: Technology stack
        target_audience: Target audience
        market_data: Market analysis data to cache
        persist_dir: Directory for persistent storage
        ttl_days: Time-to-live in days (default: 7)
    """
    client = init_market_cache(persist_dir)
    collection = client.get_collection(name="market_analysis_cache")
    
    cache_key = get_cache_key(project_description, tech_stack, target_audience)
    
    # Store metadata
    metadata = {
        "project_description": project_description[:500],  # Truncate for metadata
        "tech_stack": tech_stack[:200],
        "target_audience": target_audience,
        "cached_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(days=ttl_days)).isoformat()
    }
    
    # Serialize market data as JSON string for document
    document = json.dumps(market_data, indent=2)
    
    # Check if already exists
    try:
        existing = collection.get(ids=[cache_key])
        if existing and existing['ids']:
            # Update existing
            collection.update(
                ids=[cache_key],
                documents=[document],
                metadatas=[metadata]
            )
        else:
            # Add new
            collection.add(
                ids=[cache_key],
                documents=[document],
                metadatas=[metadata]
            )
    except Exception:
        # Add new if get fails
        collection.add(
            ids=[cache_key],
            documents=[document],
            metadatas=[metadata]
        )


def get_cached_market_analysis(
    project_description: str,
    tech_stack: str,
    target_audience: str,
    persist_dir: str = ".vectordb"
) -> Optional[Dict[str, Any]]:
    """
    Retrieve cached market analysis if available and not expired.
    
    Args:
        project_description: Project description
        tech_stack: Technology stack
        target_audience: Target audience
        persist_dir: Directory for persistent storage
        
    Returns:
        Cached market data or None if not found/expired
    """
    try:
        client = init_market_cache(persist_dir)
        collection = client.get_collection(name="market_analysis_cache")
        
        cache_key = get_cache_key(project_description, tech_stack, target_audience)
        
        # Retrieve from cache
        result = collection.get(ids=[cache_key], include=["documents", "metadatas"])
        
        if not result or not result['ids']:
            return None
        
        # Check expiration
        metadata = result['metadatas'][0]
        expires_at = datetime.fromisoformat(metadata['expires_at'])
        
        if datetime.now() > expires_at:
            # Cache expired, delete it
            collection.delete(ids=[cache_key])
            return None
        
        # Parse and return cached data
        document = result['documents'][0]
        market_data = json.loads(document)
        
        # Add cache metadata to response
        market_data['_cache_info'] = {
            'cached_at': metadata['cached_at'],
            'expires_at': metadata['expires_at'],
            'from_cache': True
        }
        
        return market_data
        
    except Exception as e:
        # If any error, return None (cache miss)
        print(f"Cache retrieval error: {e}")
        return None


def clear_expired_cache(persist_dir: str = ".vectordb") -> int:
    """
    Clear all expired cache entries.
    
    Args:
        persist_dir: Directory for persistent storage
        
    Returns:
        Number of entries cleared
    """
    try:
        client = init_market_cache(persist_dir)
        collection = client.get_collection(name="market_analysis_cache")
        
        # Get all entries
        all_entries = collection.get(include=["metadatas"])
        
        if not all_entries or not all_entries['ids']:
            return 0
        
        expired_ids = []
        now = datetime.now()
        
        for i, metadata in enumerate(all_entries['metadatas']):
            expires_at = datetime.fromisoformat(metadata['expires_at'])
            if now > expires_at:
                expired_ids.append(all_entries['ids'][i])
        
        if expired_ids:
            collection.delete(ids=expired_ids)
        
        return len(expired_ids)
        
    except Exception as e:
        print(f"Cache cleanup error: {e}")
        return 0


def get_cache_stats(persist_dir: str = ".vectordb") -> Dict[str, Any]:
    """
    Get statistics about the market analysis cache.
    
    Args:
        persist_dir: Directory for persistent storage
        
    Returns:
        Dictionary with cache statistics
    """
    try:
        client = init_market_cache(persist_dir)
        collection = client.get_collection(name="market_analysis_cache")
        
        all_entries = collection.get(include=["metadatas"])
        
        if not all_entries or not all_entries['ids']:
            return {
                "total_entries": 0,
                "expired_entries": 0,
                "valid_entries": 0
            }
        
        now = datetime.now()
        expired_count = 0
        
        for metadata in all_entries['metadatas']:
            expires_at = datetime.fromisoformat(metadata['expires_at'])
            if now > expires_at:
                expired_count += 1
        
        total = len(all_entries['ids'])
        
        return {
            "total_entries": total,
            "expired_entries": expired_count,
            "valid_entries": total - expired_count
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "total_entries": 0
        }
