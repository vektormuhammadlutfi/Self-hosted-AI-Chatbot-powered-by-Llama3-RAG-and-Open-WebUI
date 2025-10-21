"""
FastAPI backend for RAG-based chatbot.
Provides an /ask endpoint for querying documents stored in Qdrant.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging

from engine import RAGEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="Local-first RAG chatbot with LlamaIndex, Ollama, and Qdrant",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG engine
rag_engine = None


class QueryRequest(BaseModel):
    """Request model for /ask endpoint"""
    question: str
    chat_history: Optional[list] = None


class QueryResponse(BaseModel):
    """Response model for /ask endpoint"""
    answer: str
    sources: Optional[list] = None


@app.on_event("startup")
async def startup_event():
    """Initialize RAG engine on startup"""
    global rag_engine
    try:
        logger.info("Initializing RAG engine...")
        rag_engine = RAGEngine()
        logger.info("RAG engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG engine: {e}")
        # Don't fail startup - allow health checks to work
        rag_engine = None


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "status": "running",
        "service": "RAG Chatbot API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if rag_engine is None:
        raise HTTPException(status_code=503, detail="RAG engine not initialized")
    return {"status": "healthy"}


@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Ask a question and get an answer based on indexed documents.
    
    Args:
        request: QueryRequest containing the question
        
    Returns:
        QueryResponse with answer and source information
    """
    if rag_engine is None:
        raise HTTPException(
            status_code=503,
            detail="RAG engine not initialized. Please check logs."
        )
    
    try:
        logger.info(f"Processing question: {request.question}")
        
        # Query the RAG engine
        response = rag_engine.query(request.question)
        
        # Extract source information if available
        sources = []
        if hasattr(response, 'source_nodes'):
            for node in response.source_nodes:
                sources.append({
                    "text": node.node.text[:200] + "...",  # Preview
                    "score": node.score,
                    "metadata": node.node.metadata
                })
        
        return QueryResponse(
            answer=str(response),
            sources=sources if sources else None
        )
        
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get statistics about the indexed documents"""
    if rag_engine is None:
        raise HTTPException(status_code=503, detail="RAG engine not initialized")
    
    try:
        stats = rag_engine.get_collection_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
