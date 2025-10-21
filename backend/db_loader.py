"""
Database Loader - Loads data from a database table and indexes it into Qdrant.
Example: Loading FAQ data from PostgreSQL or MySQL.
"""
import os
import sys
import logging
from typing import List

from llama_index.core import Document, VectorStoreIndex, Settings, StorageContext
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseLoader:
    """Loads data from a database and indexes it into Qdrant"""
    
    def __init__(self):
        """Initialize the database loader"""
        
        # Database configuration
        self.db_type = os.getenv("DB_TYPE", "postgresql")
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_port = os.getenv("DB_PORT", "5432")
        self.db_name = os.getenv("DB_NAME", "mydb")
        self.db_user = os.getenv("DB_USER", "user")
        self.db_password = os.getenv("DB_PASSWORD", "password")
        self.db_table = os.getenv("DB_TABLE", "faq")
        
        # Ollama configuration
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
        
        # Qdrant configuration
        self.qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        self.qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        self.collection_name = os.getenv("QDRANT_COLLECTION", "documents")
        
        logger.info("Database Loader initialized")
        logger.info(f"Database: {self.db_type}://{self.db_host}:{self.db_port}/{self.db_name}")
        logger.info(f"Table: {self.db_table}")
        
        # Setup components
        self._setup_llama_index()
        self._setup_qdrant()
        self._setup_database()
    
    def _setup_llama_index(self):
        """Configure LlamaIndex settings"""
        logger.info("Setting up LlamaIndex...")
        
        self.llm = Ollama(
            model=self.ollama_model,
            base_url=self.ollama_base_url,
            temperature=0.1,
            request_timeout=120.0
        )
        
        self.embed_model = OllamaEmbedding(
            model_name=self.ollama_model,
            base_url=self.ollama_base_url,
        )
        
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model
        Settings.chunk_size = int(os.getenv("CHUNK_SIZE", "512"))
        Settings.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "50"))
        
        logger.info("LlamaIndex configured")
    
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
        
        logger.info("Qdrant connected")
    
    def _setup_database(self):
        """Create database connection"""
        logger.info("Connecting to database...")
        
        try:
            # Build connection string based on DB type
            if self.db_type == "postgresql":
                conn_str = f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
            elif self.db_type == "mysql":
                conn_str = f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            
            self.engine = create_engine(conn_str)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("Database connected successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def load_from_table(self, 
                        text_columns: List[str] = None,
                        filter_clause: str = None):
        """
        Load data from database table and index it.
        
        Args:
            text_columns: List of column names to combine as document text
                         Default: ['question', 'answer'] for FAQ table
            filter_clause: Optional SQL WHERE clause (without 'WHERE' keyword)
        """
        if text_columns is None:
            # Default for FAQ table
            text_columns = ['question', 'answer']
        
        logger.info(f"Loading data from table: {self.db_table}")
        logger.info(f"Text columns: {text_columns}")
        
        try:
            # Build SQL query
            columns_str = ', '.join(text_columns)
            query = f"SELECT id, {columns_str} FROM {self.db_table}"
            
            if filter_clause:
                query += f" WHERE {filter_clause}"
            
            logger.info(f"Executing query: {query}")
            
            # Fetch data
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                rows = result.fetchall()
            
            if not rows:
                logger.warning("No rows found in database")
                return
            
            logger.info(f"Found {len(rows)} rows")
            
            # Convert rows to LlamaIndex Documents
            documents = []
            for row in rows:
                # Combine text columns
                text_parts = [str(row[i+1]) for i in range(len(text_columns))]
                combined_text = "\n\n".join(text_parts)
                
                # Create document with metadata
                doc = Document(
                    text=combined_text,
                    metadata={
                        "source": "database",
                        "table": self.db_table,
                        "id": row[0],
                        **{text_columns[i]: str(row[i+1]) for i in range(len(text_columns))}
                    }
                )
                documents.append(doc)
            
            logger.info(f"Created {len(documents)} documents")
            
            # Index documents
            logger.info("Creating embeddings and indexing...")
            logger.info("This may take a while...")
            
            index = VectorStoreIndex.from_documents(
                documents,
                storage_context=self.storage_context,
                show_progress=True
            )
            
            logger.info("✓ Database content successfully indexed!")
            
            # Show stats
            try:
                collection_info = self.qdrant_client.get_collection(self.collection_name)
                logger.info(f"Collection: {self.collection_name}")
                logger.info(f"Total vectors: {collection_info.vectors_count}")
            except Exception as e:
                logger.warning(f"Could not retrieve stats: {e}")
                
        except Exception as e:
            logger.error(f"Error loading from database: {e}")
            raise


def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("Database Loader - RAG Chatbot")
    logger.info("=" * 60)
    
    try:
        loader = DatabaseLoader()
        
        # Example: Load FAQ data with question and answer columns
        # Customize these parameters based on your table schema
        loader.load_from_table(
            text_columns=['question', 'answer'],  # Adjust to your columns
            filter_clause=None  # Optional: "status = 'active'"
        )
        
        logger.info("=" * 60)
        logger.info("Database loading completed!")
        logger.info("=" * 60)
        
    except KeyboardInterrupt:
        logger.info("\nDatabase loading cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
