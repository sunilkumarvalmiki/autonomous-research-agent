"""
Research Agent - The main autonomous research agent implementation.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path

from ..config import get_config
from ..models.model_manager import ModelManager
from ..rag.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)


class ResearchAgent:
    """
    Autonomous research agent that can perform research tasks using
    open-source models and self-improvement mechanisms.
    """
    
    def __init__(
        self,
        model_manager: Optional[ModelManager] = None,
        knowledge_base: Optional[KnowledgeBase] = None
    ):
        """Initialize the research agent."""
        self.config = get_config()
        self.model_manager = model_manager or ModelManager()
        self.knowledge_base = knowledge_base or KnowledgeBase() if self.config.agent.enable_rag else None
        self.feedback_history: List[Dict[str, Any]] = []
        
        # Ensure feedback directory exists
        feedback_path = Path(self.config.agent.feedback_storage_path)
        feedback_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("Research agent initialized")
    
    def research(
        self,
        query: str,
        use_rag: bool = True,
        model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform research on a given query.
        
        Args:
            query: The research question or topic
            use_rag: Whether to use RAG for context
            model_name: Specific model to use (optional)
        
        Returns:
            Dictionary containing the research results
        """
        logger.info(f"Starting research on: {query}")
        
        # Analyze query to select best model
        if model_name is None:
            task_type = self._analyze_query_type(query)
            model_name = self.model_manager.select_best_model(task_type)
        
        logger.info(f"Selected model: {model_name}")
        
        # Retrieve context if RAG is enabled
        context = ""
        retrieved_docs = []
        if use_rag and self.knowledge_base is not None:
            logger.info("Retrieving relevant context from knowledge base")
            retrieved_docs = self.knowledge_base.search(query)
            context = self._format_context(retrieved_docs)
        
        # Construct prompt
        prompt = self._construct_prompt(query, context)
        
        # Generate response
        logger.info("Generating response...")
        response = self.model_manager.generate(prompt, model_name=model_name)
        
        # Prepare result
        result = {
            "query": query,
            "response": response,
            "model": model_name,
            "context_used": bool(context),
            "retrieved_documents": len(retrieved_docs),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("Research completed")
        return result
    
    def _analyze_query_type(self, query: str) -> str:
        """Analyze the query to determine its type."""
        query_lower = query.lower()
        
        # Simple heuristic-based classification
        if any(keyword in query_lower for keyword in ['code', 'program', 'function', 'debug']):
            return "code"
        elif any(keyword in query_lower for keyword in ['explain', 'why', 'how', 'reason']):
            return "reasoning"
        elif any(keyword in query_lower for keyword in ['quick', 'simple', 'brief']):
            return "fast"
        elif any(keyword in query_lower for keyword in ['story', 'creative', 'imagine']):
            return "creative"
        else:
            return "general"
    
    def _format_context(self, documents: List[Dict[str, Any]]) -> str:
        """Format retrieved documents into context string."""
        if not documents:
            return ""
        
        context_parts = ["Relevant information from knowledge base:"]
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"\n[Source {i}]")
            context_parts.append(doc['content'])
        
        return "\n".join(context_parts)
    
    def _construct_prompt(self, query: str, context: str = "") -> str:
        """Construct the prompt for the model."""
        if context:
            return f"""You are a helpful research assistant. Use the following context to answer the question accurately.

{context}

Question: {query}

Answer: Provide a comprehensive and well-reasoned answer based on the context and your knowledge."""
        else:
            return f"""You are a helpful research assistant. Answer the following question comprehensively.

Question: {query}

Answer:"""
    
    def add_to_knowledge_base(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add information to the knowledge base."""
        if self.knowledge_base is None:
            logger.warning("Knowledge base is not enabled")
            return ""
        
        logger.info("Adding content to knowledge base")
        return self.knowledge_base.add_document(content, metadata)
    
    def add_feedback(
        self,
        query: str,
        response: str,
        rating: int,
        comments: Optional[str] = None
    ) -> None:
        """
        Record feedback for self-improvement.
        
        Args:
            query: The original query
            response: The agent's response
            rating: Rating from 1-5
            comments: Optional feedback comments
        """
        feedback = {
            "query": query,
            "response": response,
            "rating": rating,
            "comments": comments,
            "timestamp": datetime.now().isoformat()
        }
        
        self.feedback_history.append(feedback)
        
        # Save feedback to disk
        self._save_feedback(feedback)
        
        # If rating is low, analyze for improvement
        if rating <= 2:
            logger.warning(f"Low rating received: {rating}/5")
            self._analyze_failure(feedback)
        
        logger.info(f"Feedback recorded: {rating}/5")
    
    def _save_feedback(self, feedback: Dict[str, Any]) -> None:
        """Save feedback to persistent storage."""
        feedback_path = Path(self.config.agent.feedback_storage_path)
        
        # Use timestamp for unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = feedback_path / f"feedback_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(feedback, f, indent=2)
    
    def _analyze_failure(self, feedback: Dict[str, Any]) -> None:
        """Analyze failed responses to identify improvement areas."""
        logger.info("Analyzing failure for self-improvement")
        
        # In a production system, this would:
        # 1. Identify common failure patterns
        # 2. Update knowledge base with corrections
        # 3. Potentially trigger fine-tuning on accumulated data
        # 4. Adjust model selection heuristics
        
        # For now, we log the analysis
        analysis = {
            "query_type": self._analyze_query_type(feedback["query"]),
            "timestamp": feedback["timestamp"],
            "rating": feedback["rating"]
        }
        
        logger.info(f"Failure analysis: {analysis}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics."""
        if not self.feedback_history:
            return {
                "total_interactions": 0,
                "average_rating": 0,
                "knowledge_base_documents": self._get_kb_count(),
                "loaded_models": self.model_manager.list_loaded_models()
            }
        
        ratings = [f["rating"] for f in self.feedback_history]
        
        return {
            "total_interactions": len(self.feedback_history),
            "average_rating": sum(ratings) / len(ratings),
            "rating_distribution": {
                str(i): ratings.count(i) for i in range(1, 6)
            },
            "knowledge_base_documents": self._get_kb_count(),
            "loaded_models": self.model_manager.list_loaded_models()
        }
    
    def _get_kb_count(self) -> int:
        """Get count of documents in knowledge base."""
        if self.knowledge_base is None:
            return 0
        
        if self.config.rag.vector_db_type == "chromadb":
            return self.knowledge_base.vector_store.count()
        elif self.config.rag.vector_db_type == "faiss":
            return len(self.knowledge_base.documents)
        
        return 0
    
    def multi_step_research(
        self,
        query: str,
        max_steps: int = 3
    ) -> Dict[str, Any]:
        """
        Perform multi-step research by breaking down complex queries.
        
        Args:
            query: Complex research question
            max_steps: Maximum number of research steps
        
        Returns:
            Dictionary with comprehensive research results
        """
        logger.info(f"Starting multi-step research: {query}")
        
        # Step 1: Decompose the query into sub-questions
        decomposition_prompt = f"""Break down the following complex question into {max_steps} simpler sub-questions that, when answered together, would fully address the original question.

Question: {query}

Provide exactly {max_steps} sub-questions, numbered 1-{max_steps}:"""
        
        decomposition = self.model_manager.generate(decomposition_prompt)
        
        # Extract sub-questions (simple parsing)
        sub_questions = []
        for line in decomposition.split('\n'):
            line = line.strip()
            if line and any(line.startswith(f"{i}.") or line.startswith(f"{i})") for i in range(1, max_steps + 1)):
                # Remove numbering
                question = line.split('.', 1)[-1].split(')', 1)[-1].strip()
                if question:
                    sub_questions.append(question)
        
        # Limit to max_steps
        sub_questions = sub_questions[:max_steps]
        
        logger.info(f"Decomposed into {len(sub_questions)} sub-questions")
        
        # Step 2: Research each sub-question
        sub_results = []
        for i, sub_q in enumerate(sub_questions, 1):
            logger.info(f"Researching sub-question {i}/{len(sub_questions)}")
            result = self.research(sub_q)
            sub_results.append({
                "question": sub_q,
                "answer": result["response"]
            })
        
        # Step 3: Synthesize final answer
        synthesis_prompt = f"""Based on the following research, provide a comprehensive answer to the original question.

Original Question: {query}

Research Findings:
"""
        for i, sr in enumerate(sub_results, 1):
            synthesis_prompt += f"\n{i}. {sr['question']}\n   {sr['answer']}\n"
        
        synthesis_prompt += f"\nSynthesized Answer to '{query}':"
        
        final_answer = self.model_manager.generate(synthesis_prompt)
        
        return {
            "query": query,
            "sub_questions": sub_questions,
            "sub_results": sub_results,
            "final_answer": final_answer,
            "steps_taken": len(sub_questions),
            "timestamp": datetime.now().isoformat()
        }
