"""Text chunking utilities for documentation and commits."""
from typing import List, Dict, Any


def chunk_text(text: str, chunk_size: int = 1500, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Target size of each chunk in characters
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at a newline or space
        if end < len(text):
            # Look for newline first
            newline_pos = text.rfind('\n', start, end)
            if newline_pos > start + chunk_size // 2:
                end = newline_pos + 1
            else:
                # Fall back to space
                space_pos = text.rfind(' ', start, end)
                if space_pos > start + chunk_size // 2:
                    end = space_pos + 1
        
        chunks.append(text[start:end].strip())
        start = end - overlap if end < len(text) else end
    
    return chunks


def chunk_documentation(docs: List[Dict[str, str]], max_chunks_per_doc: int = 5) -> List[Dict[str, Any]]:
    """
    Chunk documentation files into smaller pieces.
    
    Args:
        docs: List of documentation dicts with 'path' and 'content'
        max_chunks_per_doc: Maximum chunks to create per document
        
    Returns:
        List of chunk dicts with metadata
    """
    all_chunks = []
    
    for doc in docs:
        path = doc["path"]
        content = doc["content"]
        
        # Skip empty docs
        if not content.strip():
            continue
        
        chunks = chunk_text(content, chunk_size=1500, overlap=200)
        
        # Limit chunks per doc
        for idx, chunk in enumerate(chunks[:max_chunks_per_doc]):
            all_chunks.append({
                "id": f"doc:{path}:{idx}",
                "text": chunk,
                "metadata": {
                    "type": "doc",
                    "path": path,
                    "chunk_idx": idx,
                    "total_chunks": min(len(chunks), max_chunks_per_doc)
                }
            })
    
    return all_chunks


def chunk_commits(commits: List[Dict[str, Any]], max_files_per_commit: int = 5, max_diff_chars: int = 1000) -> List[Dict[str, Any]]:
    """
    Chunk commit data into searchable pieces.
    
    Args:
        commits: List of commit dicts with hash, message, diff, files
        max_files_per_commit: Maximum number of file chunks per commit
        max_diff_chars: Maximum characters of diff to include per file
        
    Returns:
        List of chunk dicts with metadata
    """
    all_chunks = []
    
    for commit in commits:
        sha = commit["hash"]
        message = commit["message"]
        author = commit.get("author", "Unknown")
        date = commit.get("date", "")
        files = commit.get("files", [])
        diff = commit.get("diff", "")
        
        # If no files listed but we have a diff, create a single chunk
        if not files and diff:
            chunk_text = f"Commit: {message}\nAuthor: {author}\nDate: {date}\n\nDiff:\n{diff[:max_diff_chars]}"
            all_chunks.append({
                "id": f"commit:{sha}:0",
                "text": chunk_text,
                "metadata": {
                    "type": "commit",
                    "sha": sha,
                    "message": message,
                    "author": author,
                    "date": date,
                    "file": None
                }
            })
            continue
        
        # Create per-file chunks
        for idx, file_path in enumerate(files[:max_files_per_commit]):
            # Extract diff snippet for this file if available
            diff_snippet = ""
            if diff:
                # Simple heuristic: look for the file in the diff
                if file_path in diff:
                    start = diff.find(file_path)
                    # Get a reasonable chunk around this file
                    diff_snippet = diff[start:start + max_diff_chars]
                else:
                    # Just take the first part of the diff
                    diff_snippet = diff[:max_diff_chars]
            
            chunk_text = f"Commit: {message}\nFile: {file_path}\nAuthor: {author}\nDate: {date}\n\nDiff:\n{diff_snippet}"
            
            all_chunks.append({
                "id": f"commit:{sha}:{idx}",
                "text": chunk_text,
                "metadata": {
                    "type": "commit",
                    "sha": sha,
                    "message": message,
                    "author": author,
                    "date": date,
                    "file": file_path
                }
            })
    
    return all_chunks
