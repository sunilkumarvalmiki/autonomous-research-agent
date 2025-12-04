"""
FastAPI-based REST API for the autonomous research agent.
"""

from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
import logging
from datetime import datetime

from .agents.research_agent import ResearchAgent
from .config import Config, get_config, set_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Autonomous Research Agent API",
    description="API for interacting with an autonomous research agent powered by open-source LLMs",
    version="0.1.0"
)

# Global agent instance
_agent: Optional[ResearchAgent] = None


def get_agent() -> ResearchAgent:
    """Get or create the global agent instance."""
    global _agent
    if _agent is None:
        _agent = ResearchAgent()
    return _agent


# Request/Response models
class ResearchRequest(BaseModel):
    """Request model for research endpoint."""
    query: str = Field(..., description="Research query")
    model_name: Optional[str] = Field(None, description="Specific model to use")
    use_rag: bool = Field(True, description="Whether to use RAG")


class MultiStepResearchRequest(BaseModel):
    """Request model for multi-step research."""
    query: str = Field(..., description="Complex research query")
    max_steps: int = Field(3, description="Maximum number of steps", ge=1, le=10)


class ResearchResponse(BaseModel):
    """Response model for research results."""
    query: str
    response: str
    model: str
    context_used: bool
    retrieved_documents: int
    timestamp: str


class MultiStepResearchResponse(BaseModel):
    """Response model for multi-step research."""
    query: str
    sub_questions: List[str]
    final_answer: str
    steps_taken: int
    timestamp: str


class FeedbackRequest(BaseModel):
    """Request model for feedback."""
    query: str
    response: str
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = None


class KnowledgeRequest(BaseModel):
    """Request model for adding knowledge."""
    content: str
    metadata: Optional[Dict[str, Any]] = None


class StatisticsResponse(BaseModel):
    """Response model for statistics."""
    total_interactions: int
    average_rating: float
    rating_distribution: Dict[str, int]
    knowledge_base_documents: int
    loaded_models: List[str]


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Autonomous Research Agent API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    """
    Perform research on a query.
    
    Args:
        request: Research request containing query and options
    
    Returns:
        Research results
    """
    try:
        agent = get_agent()
        result = agent.research(
            query=request.query,
            use_rag=request.use_rag,
            model_name=request.model_name
        )
        return ResearchResponse(**result)
    
    except Exception as e:
        logger.error(f"Error in research: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/research/multi-step", response_model=MultiStepResearchResponse)
async def multi_step_research(request: MultiStepResearchRequest):
    """
    Perform multi-step research on a complex query.
    
    Args:
        request: Multi-step research request
    
    Returns:
        Multi-step research results
    """
    try:
        agent = get_agent()
        result = agent.multi_step_research(
            query=request.query,
            max_steps=request.max_steps
        )
        return MultiStepResearchResponse(**result)
    
    except Exception as e:
        logger.error(f"Error in multi-step research: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback")
async def add_feedback(request: FeedbackRequest):
    """
    Add feedback for self-improvement.
    
    Args:
        request: Feedback request
    
    Returns:
        Confirmation message
    """
    try:
        agent = get_agent()
        agent.add_feedback(
            query=request.query,
            response=request.response,
            rating=request.rating,
            comments=request.comments
        )
        return {"message": "Feedback recorded successfully"}
    
    except Exception as e:
        logger.error(f"Error adding feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/knowledge")
async def add_knowledge(request: KnowledgeRequest):
    """
    Add knowledge to the knowledge base.
    
    Args:
        request: Knowledge request
    
    Returns:
        Document ID
    """
    try:
        agent = get_agent()
        doc_id = agent.add_to_knowledge_base(
            content=request.content,
            metadata=request.metadata
        )
        return {
            "message": "Knowledge added successfully",
            "document_id": doc_id
        }
    
    except Exception as e:
        logger.error(f"Error adding knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """
    Get agent statistics.
    
    Returns:
        Agent statistics
    """
    try:
        agent = get_agent()
        stats = agent.get_statistics()
        return StatisticsResponse(**stats)
    
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models")
async def list_models():
    """
    List available models.
    
    Returns:
        List of model names
    """
    try:
        agent = get_agent()
        models = agent.model_manager.list_models()
        loaded = agent.model_manager.list_loaded_models()
        
        return {
            "available_models": models,
            "loaded_models": loaded
        }
    
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/config")
async def get_configuration():
    """
    Get current configuration.
    
    Returns:
        Current configuration
    """
    try:
        config = get_config()
        return config.model_dump()
    
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
