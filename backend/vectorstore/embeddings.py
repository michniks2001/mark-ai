"""FastEmbed wrapper for Chroma embedding function."""
from typing import cast
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
from fastembed import TextEmbedding


class FastEmbedEmbeddingFunction(EmbeddingFunction[Documents]):
    """Chroma-compatible embedding function using FastEmbed."""
    
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        """
        Initialize FastEmbed embedding function.
        
        Args:
            model_name: FastEmbed model name. Default is a lightweight, fast model.
                       Other options: "sentence-transformers/all-MiniLM-L6-v2"
        """
        self._model = TextEmbedding(model_name=model_name)
    
    def __call__(self, input: Documents) -> Embeddings:
        """
        Generate embeddings for input documents.
        
        Args:
            input: List of text documents
            
        Returns:
            List of embedding vectors
        """
        # FastEmbed returns a generator of numpy arrays
        embeddings = list(self._model.embed(input))
        # Convert to list of lists for Chroma
        return [embedding.tolist() for embedding in embeddings]
