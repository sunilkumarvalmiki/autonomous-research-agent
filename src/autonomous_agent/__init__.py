"""
Autonomous Research Agent Package
An intelligent agent system that leverages open-source LLMs with self-improvement capabilities.
"""

__version__ = "0.1.0"
__author__ = "Autonomous Research Agent Team"

from .models.model_manager import ModelManager
from .agents.research_agent import ResearchAgent
from .rag.knowledge_base import KnowledgeBase

__all__ = [
    "ModelManager",
    "ResearchAgent",
    "KnowledgeBase",
]
