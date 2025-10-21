"""
Document Loader - Loads documents from /data/docs and indexes them into Qdrant.
Supports PDF, TXT, and DOCX formats.
"""
import os
import sys
from pathlib import Path
import logging

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocumentLoader:
    """Loads and indexes documents into Qdrant vector store"""
    
    def __init__(self, docs_path: str = "/data/docs"):
        """
        Initialize the document loader.
        
        Args:
            docs_path: Path to the directory containing documents
        """
        self.docs_path = docs_path
        
        # Load configuration
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
        self.qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        self.qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        self.collection_name = os.getenv("QDRANT_COLLECTION", "documents")
        
        logger.info(f"Document loader initialized")
        logger.info(f"Docs path: {self.docs_path}")
        logger.info(f"Ollama: {self.ollama_base_url} (model: {self.ollama_model})")
        logger.info(f"Qdrant: {self.qdrant_host}:{self.qdrant_port}")
        
        # Initialize LLM and embeddings
        self._setup_llama_index()
        
        # Initialize Qdrant
        self._setup_qdrant()
    
    def _setup_llama_index(self):
        """Configure LlamaIndex settings"""
        logger.info("Setting up LlamaIndex...")
        
        # Initialize Ollama LLM
        self.llm = Ollama(
            model=self.ollama_model,
            base_url=self.ollama_base_url,
            temperature=0.1,
            request_timeout=120.0
        )
        
        # Initialize embeddings
        self.embed_model = OllamaEmbedding(
            model_name=self.ollama_model,
            base_url=self.ollama_base_url,
        )
        
        # Configure global settings
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model
        Settings.chunk_size = int(os.getenv("CHUNK_SIZE", "512"))
        Settings.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "50"))
        
        logger.info("LlamaIndex configured successfully")
    
    def _setup_qdrant(self):
        """Initialize Qdrant client and vector store"""
        logger.info("Connecting to Qdrant...")
        
        self.qdrant_client = QdrantClient(
            host=self.qdrant_host,
            port=self.qdrant_port
        )
        
        self.vector_store = QdrantVectorStore(
            client=self.qdrant_client,
            collection_name=self.collection_name
        )
        
        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )
        
        logger.info("Qdrant connection established")
    
    def load_documents(self):
        """
        Load documents from the docs directory and index them.
        """
        # Check if docs path exists
        if not os.path.exists(self.docs_path):
            logger.error(f"Documents path does not exist: {self.docs_path}")
            logger.info(f"Creating directory: {self.docs_path}")
            os.makedirs(self.docs_path, exist_ok=True)
            logger.warning("No documents to load. Add files to /data/docs and run again.")
            return
        
        # Count files
        file_extensions = ['.pdf', '.txt', '.docx']
        files = []
        for ext in file_extensions:
            files.extend(list(Path(self.docs_path).rglob(f'*{ext}')))
        
        if not files:
            logger.warning(f"No documents found in {self.docs_path}")
            logger.info(f"Supported formats: {', '.join(file_extensions)}")
            return
        
        logger.info(f"Found {len(files)} document(s) to process")
        
        # Load documents using SimpleDirectoryReader
        logger.info("Loading documents...")
        try:
            reader = SimpleDirectoryReader(
                input_dir=self.docs_path,
                recursive=True,
                required_exts=['.pdf', '.txt', '.docx']
            )
            documents = reader.load_data()
            logger.info(f"Loaded {len(documents)} document chunks")
            
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            return
        
        # Create index and store in Qdrant
        logger.info("Creating embeddings and indexing documents...")
        logger.info("This may take a while depending on document size...")
        
        try:
            index = VectorStoreIndex.from_documents(
                documents,
                storage_context=self.storage_context,
                show_progress=True
            )
            logger.info("✓ Documents successfully indexed into Qdrant!")
            
            # Show stats
            try:
                collection_info = self.qdrant_client.get_collection(self.collection_name)
                logger.info(f"Collection: {self.collection_name}")
                logger.info(f"Total vectors: {collection_info.vectors_count}")
                logger.info(f"Total points: {collection_info.points_count}")
            except Exception as e:
                logger.warning(f"Could not retrieve collection stats: {e}")
                
        except Exception as e:
            logger.error(f"Error indexing documents: {e}")
            raise


def main():
    """Main entry point for the document loader"""
    logger.info("=" * 60)
    logger.info("Document Loader - RAG Chatbot")
    logger.info("=" * 60)
    
    # Determine docs path based on environment
    if os.path.exists("/data/docs"):
        docs_path = "/data/docs"
    elif os.path.exists("../data/docs"):
        docs_path = "../data/docs"
    else:
        docs_path = "./data/docs"
    
    try:
        loader = DocumentLoader(docs_path=docs_path)
        loader.load_documents()
        logger.info("=" * 60)
        logger.info("Document loading completed!")
        logger.info("=" * 60)
        
    except KeyboardInterrupt:
        logger.info("\nDocument loading cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
