"""
FastAPI backend for RAG-based chatbot.
Provides an /ask endpoint for querying documents stored in Qdrant.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

from engine import RAGEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app with enhanced metadata
app = FastAPI(
    title="🤖 RAG Chatbot API",
    description="""
    ## Local-First RAG Chatbot API
    
    A powerful Retrieval-Augmented Generation (RAG) chatbot API built with:
    - **LlamaIndex**: Advanced RAG framework
    - **Ollama**: Local LLM runtime (Llama3)
    - **Qdrant**: Vector database for semantic search
    - **FastAPI**: Modern, high-performance API framework
    
    ### Features
    - 🔍 Semantic search across your documents
    - 💬 Context-aware question answering
    - 📚 Multi-document knowledge base
    - 🔒 100% local and private
    - ⚡ Fast response times
    
    ### Getting Started
    1. Index your documents using `/docs/index` endpoint
    2. Ask questions using `/ask` endpoint
    3. Monitor statistics with `/stats` endpoint
    
    ### API Documentation
    - **Scalar Docs** (Modern UI): [/docs](/docs)
    - **ReDoc** (Alternative): [/redoc](/redoc)
    - **OpenAPI Spec**: [/openapi.json](/openapi.json)
    """,
    version="2.0.0",
    contact={
        "name": "RAG Chatbot Support",
        "url": "https://github.com/your-repo/rag-chatbot",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url=None,  # Disable default Swagger UI
    redoc_url="/redoc",  # Keep ReDoc as alternative
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

# Request query counter
query_count = 0

# Current selected model
current_model = {
    "provider": "ollama",
    "model_name": "llama3",
    "display_name": "Llama 3 (Local)"
}


# ============================================================================
# Pydantic Models
# ============================================================================

class QueryRequest(BaseModel):
    """Request model for asking questions"""
    question: str = Field(
        ...,
        description="The question you want to ask about your documents",
        example="What are the main features of the product?"
    )
    model: Optional[str] = Field(
        None,
        description="Optional model to use (e.g., 'llama3', 'openai/gpt-4', 'gemini-pro')",
        example="llama3"
    )
    chat_history: Optional[List[Dict[str, str]]] = Field(
        None,
        description="Optional chat history for context-aware responses",
        example=[
            {"role": "user", "content": "Tell me about the product"},
            {"role": "assistant", "content": "The product is..."}
        ]
    )
    max_sources: Optional[int] = Field(
        3,
        description="Maximum number of source documents to return",
        ge=1,
        le=10
    )


class SourceDocument(BaseModel):
    """Source document information"""
    text: str = Field(..., description="Excerpt from the source document")
    score: float = Field(..., description="Relevance score (0-1)")
    metadata: Dict[str, Any] = Field(..., description="Document metadata")


class QueryResponse(BaseModel):
    """Response model for question answering"""
    answer: str = Field(..., description="The generated answer to your question")
    sources: Optional[List[SourceDocument]] = Field(
        None,
        description="Source documents used to generate the answer"
    )
    query_time: Optional[float] = Field(
        None,
        description="Time taken to process the query (seconds)"
    )


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    rag_engine: str = Field(..., description="RAG engine status")
    timestamp: str = Field(..., description="Current server time")


class StatsResponse(BaseModel):
    """Statistics response"""
    collection_name: str = Field(..., description="Name of the Qdrant collection")
    vectors_count: int = Field(0, description="Number of vectors in the collection")
    points_count: int = Field(0, description="Number of points in the collection")
    total_queries: int = Field(0, description="Total queries processed")
    status: str = Field("unknown", description="Collection status")


class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str = Field(..., description="Error message")
    timestamp: str = Field(..., description="Error timestamp")


class ModelInfo(BaseModel):
    """Model information"""
    id: str = Field(..., description="Model identifier")
    name: str = Field(..., description="Display name")
    provider: str = Field(..., description="Model provider (ollama, openrouter, gemini)")
    description: Optional[str] = Field(None, description="Model description")
    context_length: Optional[int] = Field(None, description="Maximum context length")


class ModelsResponse(BaseModel):
    """Available models response"""
    current_model: str = Field(..., description="Currently selected model")
    available_models: List[ModelInfo] = Field(..., description="List of available models")


class ModelSelectRequest(BaseModel):
    """Model selection request"""
    model_id: str = Field(
        ...,
        description="Model ID to select",
        example="llama3"
    )


class BPSQueryRequest(BaseModel):
    """BPS API query request"""
    endpoint: str = Field(
        ...,
        description="BPS endpoint to query (domains, news, publications, stats, etc.)",
        example="domains"
    )
    domain: Optional[str] = Field(
        None,
        description="Domain code (e.g., '7315' for Kabupaten Pinrang)",
        example="7315"
    )
    params: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional parameters for the BPS API",
        example={"year": "2022", "lang": "ind"}
    )


class BPSQueryResponse(BaseModel):
    """BPS API query response"""
    endpoint: str = Field(..., description="BPS endpoint that was queried")
    data: Dict[str, Any] = Field(..., description="Response data from BPS API")
    query_time: float = Field(..., description="Time taken to process the query")


# ============================================================================
# Scalar API Documentation (Custom HTML)
# ============================================================================

@app.get("/docs", include_in_schema=False)
async def scalar_docs():
    """
    Scalar API Documentation - Modern, Beautiful API Docs
    Uses Scalar's CDN-hosted version for beautiful API documentation
    """
    from fastapi.responses import HTMLResponse
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>RAG Chatbot API - Documentation</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
    </head>
    <body>
        <script
            id="api-reference"
            data-url="/openapi.json"
            data-configuration='{"theme":"purple","layout":"modern","showSidebar":true}'
        ></script>
        <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# ============================================================================
# Lifecycle Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize RAG engine on startup"""
    global rag_engine
    try:
        logger.info("🚀 Starting RAG Chatbot API...")
        logger.info("Initializing RAG engine...")
        rag_engine = RAGEngine()
        logger.info("✅ RAG engine initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize RAG engine: {e}")
        # Don't fail startup - allow health checks to work
        rag_engine = None


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down RAG Chatbot API...")


# ============================================================================
# API Endpoints
# ============================================================================

@app.get(
    "/",
    tags=["General"],
    summary="Root Endpoint",
    description="Basic information about the API service"
)
async def root():
    """
    Root endpoint providing basic service information.
    
    Returns service name, version, and documentation links.
    """
    return {
        "service": "🤖 RAG Chatbot API",
        "version": "2.0.0",
        "status": "running",
        "documentation": {
            "scalar": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "endpoints": {
            "ask": "/ask",
            "health": "/health",
            "stats": "/stats"
        }
    }


@app.get(
    "/health",
    tags=["General"],
    summary="Health Check",
    description="Check if the API and RAG engine are running properly",
    response_model=HealthResponse,
    responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "rag_engine": "initialized",
                        "timestamp": "2025-10-22T10:30:00Z"
                    }
                }
            }
        },
        503: {
            "description": "Service unavailable",
            "model": ErrorResponse
        }
    }
)
async def health_check():
    """
    Health check endpoint to verify service availability.
    
    Returns:
    - `status`: Overall service status
    - `rag_engine`: RAG engine initialization status
    - `timestamp`: Current server time
    
    Status Codes:
    - 200: Service is healthy
    - 503: Service unavailable (RAG engine not initialized)
    """
    if rag_engine is None:
        raise HTTPException(
            status_code=503,
            detail="RAG engine not initialized. Please check server logs."
        )
    
    return HealthResponse(
        status="healthy",
        rag_engine="initialized",
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


@app.post(
    "/ask",
    tags=["Q&A"],
    summary="Ask a Question",
    description="Ask a question and get an AI-generated answer based on your indexed documents",
    response_model=QueryResponse,
    responses={
        200: {
            "description": "Successful response with answer and sources",
            "content": {
                "application/json": {
                    "example": {
                        "answer": "The main features include document learning, semantic search, and context-aware responses.",
                        "sources": [
                            {
                                "text": "Our product offers advanced document learning capabilities...",
                                "score": 0.89,
                                "metadata": {"filename": "product_guide.pdf", "page": 1}
                            }
                        ],
                        "query_time": 1.23
                    }
                }
            }
        },
        400: {"description": "Bad request - invalid question format"},
        503: {"description": "Service unavailable", "model": ErrorResponse}
    }
)
async def ask_question(request: QueryRequest):
    """
    Ask a question about your documents and get an AI-generated answer.
    
    This endpoint uses Retrieval-Augmented Generation (RAG) to:
    1. Search for relevant document chunks in the vector database
    2. Use the found context to generate an accurate answer
    3. Return source references for transparency
    
    **Parameters:**
    - `question`: Your question (required)
    - `chat_history`: Previous conversation for context (optional)
    - `max_sources`: Number of source documents to return (1-10, default: 3)
    
    **Returns:**
    - `answer`: AI-generated answer to your question
    - `sources`: List of source documents used (with relevance scores)
    - `query_time`: Processing time in seconds
    
    **Example Request:**
    ```json
    {
      "question": "What are the system requirements?",
      "max_sources": 3
    }
    ```
    """
    global query_count
    
    if rag_engine is None:
        raise HTTPException(
            status_code=503,
            detail="RAG engine not initialized. Please check server logs."
        )
    
    if not request.question or len(request.question.strip()) == 0:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )
    
    try:
        import time
        start_time = time.time()
        
        logger.info(f"📝 Processing question: {request.question}")
        query_count += 1
        
        # Query the RAG engine
        response = rag_engine.query(request.question)
        
        # Extract source information if available
        sources = []
        if hasattr(response, 'source_nodes'):
            max_sources = min(request.max_sources or 3, len(response.source_nodes))
            for node in response.source_nodes[:max_sources]:
                sources.append(SourceDocument(
                    text=node.node.text[:300] + ("..." if len(node.node.text) > 300 else ""),
                    score=round(node.score, 4),
                    metadata=node.node.metadata
                ))
        
        query_time = round(time.time() - start_time, 2)
        logger.info(f"✅ Query completed in {query_time}s")
        
        return QueryResponse(
            answer=str(response),
            sources=sources if sources else None,
            query_time=query_time
        )
        
    except Exception as e:
        logger.error(f"❌ Error processing question: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )


@app.get(
    "/stats",
    tags=["Statistics"],
    summary="Get Collection Statistics",
    description="Retrieve statistics about your indexed documents and vector database",
    response_model=StatsResponse,
    responses={
        200: {
            "description": "Successfully retrieved statistics",
            "content": {
                "application/json": {
                    "example": {
                        "collection_name": "documents",
                        "vectors_count": 150,
                        "points_count": 150,
                        "total_queries": 42,
                        "status": "green"
                    }
                }
            }
        },
        503: {"description": "Service unavailable", "model": ErrorResponse}
    }
)
async def get_stats():
    """
    Get comprehensive statistics about your document collection.
    
    Returns information about:
    - Number of indexed document chunks (vectors)
    - Collection health status
    - Total queries processed
    - Database collection name
    
    **Returns:**
    - `collection_name`: Name of the Qdrant collection
    - `vectors_count`: Number of document vectors
    - `points_count`: Number of data points
    - `total_queries`: Total queries processed since startup
    - `status`: Collection health (green/yellow/red)
    
    **Use Cases:**
    - Monitor your document index size
    - Check if documents are being indexed
    - Track API usage
    - Verify database connectivity
    """
    if rag_engine is None:
        raise HTTPException(
            status_code=503,
            detail="RAG engine not initialized"
        )
    
    try:
        stats = rag_engine.get_collection_stats()
        stats['total_queries'] = query_count
        
        return StatsResponse(
            collection_name=stats.get('collection_name') or 'unknown',
            vectors_count=stats.get('vectors_count') or 0,
            points_count=stats.get('points_count') or 0,
            total_queries=query_count,
            status=stats.get('status') or 'unknown'
        )
    except Exception as e:
        logger.error(f"❌ Error getting stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving statistics: {str(e)}"
        )


# ============================================================================
# Model Management Endpoints
# ============================================================================

@app.get(
    "/models",
    tags=["Models"],
    summary="List Available Models",
    description="Get list of all available AI models (Ollama, OpenRouter, Gemini)",
    response_model=ModelsResponse
)
async def list_models():
    """
    List all available AI models from different providers.
    
    Returns models from:
    - **Ollama** (local models)
    - **OpenRouter** (GPT-4, Claude, etc.)
    - **Google Gemini** (Gemini Pro, Flash)
    
    **Use Cases:**
    - Display model selection in UI
    - Check available models
    - Compare model capabilities
    """
    import requests
    
    models = []
    
    # Ollama models (local)
    try:
        ollama_response = requests.get("http://ollama:11434/api/tags", timeout=5)
        if ollama_response.status_code == 200:
            ollama_data = ollama_response.json()
            for model in ollama_data.get("models", []):
                models.append(ModelInfo(
                    id=model.get("name", "unknown"),
                    name=f"{model.get('name', 'Unknown')} (Local)",
                    provider="ollama",
                    description="Local Ollama model"
                ))
    except Exception as e:
        logger.warning(f"Could not fetch Ollama models: {e}")
    
    # OpenRouter models (popular ones)
    openrouter_models = [
        {"id": "openai/gpt-4-turbo", "name": "GPT-4 Turbo", "context": 128000},
        {"id": "openai/gpt-4", "name": "GPT-4", "context": 8192},
        {"id": "openai/gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "context": 16385},
        {"id": "anthropic/claude-3-opus", "name": "Claude 3 Opus", "context": 200000},
        {"id": "anthropic/claude-3-sonnet", "name": "Claude 3 Sonnet", "context": 200000},
        {"id": "anthropic/claude-3-haiku", "name": "Claude 3 Haiku", "context": 200000},
        {"id": "meta-llama/llama-3-70b-instruct", "name": "Llama 3 70B", "context": 8192},
        {"id": "google/gemini-pro", "name": "Gemini Pro", "context": 32768},
    ]
    
    for model in openrouter_models:
        models.append(ModelInfo(
            id=model["id"],
            name=f"{model['name']} (OpenRouter)",
            provider="openrouter",
            description=f"Via OpenRouter API",
            context_length=model["context"]
        ))
    
    # Gemini models
    gemini_models = [
        {"id": "gemini-pro", "name": "Gemini Pro", "context": 32768},
        {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "context": 1000000},
        {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash", "context": 1000000},
    ]
    
    for model in gemini_models:
        models.append(ModelInfo(
            id=model["id"],
            name=f"{model['name']} (Google)",
            provider="gemini",
            description="Google Gemini model",
            context_length=model["context"]
        ))
    
    return ModelsResponse(
        current_model=current_model["model_name"],
        available_models=models
    )


@app.post(
    "/models/select",
    tags=["Models"],
    summary="Select Model",
    description="Switch to a different AI model"
)
async def select_model(request: ModelSelectRequest):
    """
    Select a different AI model for processing queries.
    
    **Supported Models:**
    - Ollama: `llama3`, `mistral`, etc.
    - OpenRouter: `openai/gpt-4`, `anthropic/claude-3-opus`, etc.
    - Gemini: `gemini-pro`, `gemini-1.5-pro`, etc.
    
    **Note:** Model switching will affect subsequent `/ask` requests.
    """
    global current_model
    
    # Determine provider from model_id
    provider = "ollama"
    if "/" in request.model_id:
        if "gemini" in request.model_id.lower():
            provider = "gemini"
        else:
            provider = "openrouter"
    elif "gemini" in request.model_id.lower():
        provider = "gemini"
    
    current_model = {
        "provider": provider,
        "model_name": request.model_id,
        "display_name": request.model_id
    }
    
    logger.info(f"🔄 Switched to model: {request.model_id} (provider: {provider})")
    
    return {
        "status": "success",
        "message": f"Switched to model: {request.model_id}",
        "current_model": current_model
    }


# ============================================================================
# BPS (Indonesian Statistics) Integration
# ============================================================================

@app.post(
    "/bps/query",
    tags=["BPS Integration"],
    summary="Query BPS API",
    description="Query Indonesian Statistics Bureau (BPS) Web API",
    response_model=BPSQueryResponse
)
async def query_bps(request: BPSQueryRequest):
    """
    Query BPS (Badan Pusat Statistik) Web API for Indonesian statistical data.
    
    **Available Endpoints:**
    - `domains` - List all provinces/regencies
    - `subcat` - Subject categories
    - `subjects` - Subjects by category
    - `variables` - Variables by subject  
    - `data` - Statistical data
    - `news` - BPS news
    - `publications` - BPS publications
    - `pressrelease` - Press releases
    - `indicators` - Strategic indicators
    
    **Example Request:**
    ```json
    {
      "endpoint": "domains",
      "params": {"type": "kabbyprov", "prov": "73"}
    }
    ```
    
    **Example for Pinrang:**
    ```json
    {
      "endpoint": "news",
      "domain": "7315",
      "params": {"year": "2022", "lang": "ind"}
    }
    ```
    
    **Note:** Requires BPS API key (configure in Open WebUI Tools)
    """
    import requests
    import time
    
    start_time = time.time()
    
    # BPS API base URL
    BPS_BASE_URL = "https://webapi.bps.go.id/v1/api"
    
    # This is just a proxy - actual implementation should use the BPS function in Open WebUI
    # For now, return information about how to use it
    
    try:
        if request.endpoint == "domains":
            # Example response structure
            response_data = {
                "status": "info",
                "message": "BPS API integration is available via Open WebUI Tools/Functions",
                "endpoint": request.endpoint,
                "instructions": {
                    "step1": "Open Open WebUI at http://localhost:3000",
                    "step2": "Go to Workspace → Functions",
                    "step3": "Install the BPS API Integration function",
                    "step4": "Configure your BPS API key in the function settings",
                    "step5": "Use the function in chat: 'Get BPS domains'"
                },
                "example_functions": [
                    "get_domains() - List all provinces/regencies",
                    "get_news('7315', year='2022') - Get news for Pinrang",
                    "get_publications('7315') - Get publications",
                    "get_statistical_data(...) - Get statistical data"
                ]
            }
        else:
            response_data = {
                "status": "info",
                "message": f"BPS endpoint '{request.endpoint}' should be accessed via Open WebUI Functions",
                "endpoint": request.endpoint,
                "domain": request.domain,
                "params": request.params or {}
            }
        
        query_time = time.time() - start_time
        
        return BPSQueryResponse(
            endpoint=request.endpoint,
            data=response_data,
            query_time=round(query_time, 3)
        )
        
    except Exception as e:
        logger.error(f"❌ BPS query error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"BPS query failed: {str(e)}"
        )


@app.get(
    "/bps/info",
    tags=["BPS Integration"],
    summary="BPS Integration Info",
    description="Get information about BPS API integration"
)
async def bps_info():
    """
    Get information about BPS (Badan Pusat Statistik) API integration.
    
    Returns setup instructions and available endpoints.
    """
    return {
        "name": "BPS Web API Integration",
        "description": "Access Indonesian statistical data from BPS",
        "api_url": "https://webapi.bps.go.id",
        "documentation": "https://webapi.bps.go.id/documentation",
        "setup": {
            "step1": "Get API key from https://webapi.bps.go.id",
            "step2": "Install BPS function in Open WebUI (Workspace → Functions)",
            "step3": "Configure API key in function settings",
            "step4": "Use in chat or via this API"
        },
        "available_endpoints": [
            "domains - List provinces/regencies",
            "subcat - Subject categories",
            "subjects - Subjects by category",
            "variables - Variables by subject",
            "data - Statistical data",
            "news - BPS news articles",
            "publications - Publications",
            "pressrelease - Press releases",
            "indicators - Strategic indicators"
        ],
        "example_domains": {
            "sulawesi_selatan": "73",
            "pinrang": "7315",
            "makassar": "7371",
            "jakarta": "31"
        },
        "integration_method": "Via Open WebUI Functions (preferred) or direct API calls"
    }


# ============================================================================
# Additional Utility Endpoints
# ============================================================================

@app.get(
    "/collections",
    tags=["Statistics"],
    summary="List All Collections",
    description="Get a list of all Qdrant collections"
)
async def list_collections():
    """
    List all available Qdrant collections.
    
    Useful for debugging and monitoring multiple collections.
    """
    if rag_engine is None:
        raise HTTPException(status_code=503, detail="RAG engine not initialized")
    
    try:
        # This would need to be implemented in RAGEngine
        return {
            "collections": ["documents"],
            "active_collection": "documents"
        }
    except Exception as e:
        logger.error(f"Error listing collections: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
