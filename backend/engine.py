"""
RAG Engine - Connects LlamaIndex with Ollama and Qdrant.
Handles document indexing and querying.
"""
import os
from typing import Optional
import logging

from llama_index.core import VectorStoreIndex, Settings, StorageContext
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    RAG Engine for document querying using LlamaIndex, Ollama, and Qdrant.
    """
    
    def __init__(self):
        """Initialize the RAG engine with Ollama and Qdrant"""
        
        # Load configuration from environment
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
        self.qdrant_host = os.getenv("QDRANT_HOST", "qdrant")
        self.qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        self.collection_name = os.getenv("QDRANT_COLLECTION", "documents")
        
        logger.info(f"Initializing RAG engine with Ollama at {self.ollama_base_url}")
        logger.info(f"Using model: {self.ollama_model}")
        logger.info(f"Qdrant at {self.qdrant_host}:{self.qdrant_port}")
        
        # Initialize Ollama LLM
        self.llm = Ollama(
            model=self.ollama_model,
            base_url=self.ollama_base_url,
            temperature=0.1,
            request_timeout=120.0
        )
        
        # Initialize Ollama embeddings
        self.embed_model = OllamaEmbedding(
            model_name=self.ollama_model,
            base_url=self.ollama_base_url,
        )
        
        # Configure LlamaIndex settings globally
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model
        Settings.chunk_size = int(os.getenv("CHUNK_SIZE", "512"))
        Settings.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "50"))
        
        # Initialize Qdrant client
        self.qdrant_client = QdrantClient(
            host=self.qdrant_host,
            port=self.qdrant_port
        )
        
        # Initialize vector store
        self.vector_store = QdrantVectorStore(
            client=self.qdrant_client,
            collection_name=self.collection_name
        )
        
        # Create storage context
        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )
        
        # Initialize or load index
        self.index = self._initialize_index()
        
        # Create query engine
        self.query_engine = self.index.as_query_engine(
            similarity_top_k=5,
            response_mode="compact"
        )
        
        logger.info("RAG engine initialized successfully")
    
    def _initialize_index(self) -> VectorStoreIndex:
        """
        Initialize or load the vector store index.
        
        Returns:
            VectorStoreIndex instance
        """
        try:
            # Check if collection exists
            try:
                collections = self.qdrant_client.get_collections().collections
                collection_exists = any(c.name == self.collection_name for c in collections)
            except Exception:
                # If we can't check collections, assume it doesn't exist
                collection_exists = False
            
            if collection_exists:
                logger.info(f"Loading existing collection: {self.collection_name}")
                # Load existing index
                index = VectorStoreIndex.from_vector_store(
                    vector_store=self.vector_store,
                    storage_context=self.storage_context
                )
            else:
                logger.info(f"Collection {self.collection_name} does not exist yet")
                logger.info("Index will be created when documents are loaded")
                # Create empty index
                index = VectorStoreIndex.from_documents(
                    [],
                    storage_context=self.storage_context
                )
            
            return index
            
        except Exception as e:
            logger.error(f"Error initializing index: {e}")
            # Create new empty index as fallback
            return VectorStoreIndex.from_documents(
                [],
                storage_context=self.storage_context
            )
    
    def query(self, question: str):
        """
        Query the RAG engine with a question.
        
        Args:
            question: User's question
            
        Returns:
            Response from the query engine
        """
        try:
            response = self.query_engine.query(question)
            return response
        except Exception as e:
            logger.error(f"Error during query: {e}")
            raise
    
    def get_collection_stats(self) -> dict:
        """
        Get statistics about the vector collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            return {
                "collection_name": self.collection_name,
                "vectors_count": collection_info.vectors_count,
                "points_count": collection_info.points_count,
                "status": collection_info.status
            }
        except Exception as e:
            logger.warning(f"Could not get collection stats: {e}")
            return {
                "collection_name": self.collection_name,
                "error": str(e)
            }
