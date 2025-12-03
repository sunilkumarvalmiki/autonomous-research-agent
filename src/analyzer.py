"""
Analyzer module for LLM-based synthesis of research findings.
Supports Groq (Llama), HuggingFace, and Google Gemini APIs.
"""

import os
import logging
from typing import List, Dict, Any, Optional
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GroqAnalyzer:
    """Analyzer using Groq API (Llama 3.3 70B)."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        self.client = None
        
        if self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
                logger.info("Groq API initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Groq: {e}")
    
    def analyze(self, data: Dict[str, List[Dict[str, Any]]], query: str) -> Dict[str, Any]:
        """Analyze research data using Groq."""
        if not self.client:
            logger.warning("Groq client not available")
            return self._fallback_analysis(data, query)
        
        try:
            # Prepare context from data
            context = self._prepare_context(data)
            
            prompt = f"""You are a research analyst. Analyze the following research data about "{query}" and provide a comprehensive synthesis.

Research Data:
{context}

Provide a structured analysis with:
1. Key Findings (3-5 main points)
2. Trends and Patterns
3. Notable Papers/Projects (if applicable)
4. Recommendations for further exploration
5. Summary

Format your response as JSON with these sections."""

            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Try to parse as JSON, otherwise return as text
            try:
                analysis = json.loads(content)
            except:
                analysis = {
                    "key_findings": [],
                    "trends": content,
                    "notable_items": [],
                    "recommendations": [],
                    "summary": content[:500]
                }
            
            logger.info("Groq analysis completed")
            return analysis
            
        except Exception as e:
            logger.error(f"Error with Groq analysis: {e}")
            return self._fallback_analysis(data, query)
    
    def _prepare_context(self, data: Dict[str, List[Dict[str, Any]]], max_items: int = 20) -> str:
        """Prepare context from scraped data."""
        context = []
        
        if data.get('papers'):
            context.append("PAPERS:")
            for i, paper in enumerate(data['papers'][:max_items], 1):
                context.append(f"{i}. {paper.get('title', 'N/A')}")
                context.append(f"   Authors: {', '.join(paper.get('authors', [])[:3])}")
                context.append(f"   Summary: {paper.get('summary', '')[:200]}")
        
        if data.get('repositories'):
            context.append("\nREPOSITORIES:")
            for i, repo in enumerate(data['repositories'][:max_items], 1):
                context.append(f"{i}. {repo.get('title', 'N/A')} ({repo.get('stars', 0)} stars)")
                context.append(f"   {repo.get('description', '')[:150]}")
        
        if data.get('news'):
            context.append("\nNEWS & ARTICLES:")
            for i, item in enumerate(data['news'][:max_items], 1):
                context.append(f"{i}. {item.get('title', 'N/A')}")
        
        if data.get('discussions'):
            context.append("\nDISCUSSIONS:")
            for i, disc in enumerate(data['discussions'][:max_items], 1):
                context.append(f"{i}. {disc.get('title', 'N/A')} ({disc.get('score', 0)} score)")
        
        return "\n".join(context)[:8000]  # Limit context size
    
    def _fallback_analysis(self, data: Dict[str, List[Dict[str, Any]]], query: str) -> Dict[str, Any]:
        """Fallback analysis without LLM."""
        return {
            "key_findings": [
                f"Found {len(data.get('papers', []))} academic papers",
                f"Found {len(data.get('repositories', []))} GitHub repositories",
                f"Found {len(data.get('news', []))} news articles",
                f"Found {len(data.get('discussions', []))} discussions"
            ],
            "trends": f"Research on {query} shows active development across multiple platforms.",
            "notable_items": self._get_top_items(data),
            "recommendations": [
                "Review the top papers for academic insights",
                "Explore trending repositories for practical implementations",
                "Follow ongoing discussions for community perspectives"
            ],
            "summary": f"Comprehensive research on '{query}' reveals significant activity across academic papers, open-source projects, and community discussions."
        }
    
    def _get_top_items(self, data: Dict[str, List[Dict[str, Any]]]) -> List[str]:
        """Get top items from each category."""
        items = []
        
        if data.get('papers'):
            items.append(f"Paper: {data['papers'][0].get('title', 'N/A')}")
        
        if data.get('repositories'):
            top_repo = max(data['repositories'], key=lambda x: x.get('stars', 0), default=None)
            if top_repo:
                items.append(f"Repository: {top_repo.get('title', 'N/A')} ({top_repo.get('stars', 0)} stars)")
        
        return items


class HuggingFaceAnalyzer:
    """Analyzer using HuggingFace Inference API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('HUGGINGFACE_API_KEY')
        self.client = None
        
        if self.api_key:
            try:
                from huggingface_hub import InferenceClient
                self.client = InferenceClient(token=self.api_key)
                logger.info("HuggingFace API initialized")
            except Exception as e:
                logger.error(f"Failed to initialize HuggingFace: {e}")
    
    def analyze(self, data: Dict[str, List[Dict[str, Any]]], query: str) -> Dict[str, Any]:
        """Analyze research data using HuggingFace."""
        if not self.client:
            logger.warning("HuggingFace client not available")
            return GroqAnalyzer()._fallback_analysis(data, query)
        
        try:
            context = GroqAnalyzer()._prepare_context(data)
            
            prompt = f"Analyze this research data about '{query}' and provide key findings:\n{context[:2000]}"
            
            response = self.client.text_generation(
                prompt,
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                max_new_tokens=1000
            )
            
            return {
                "key_findings": [],
                "trends": response,
                "notable_items": [],
                "recommendations": [],
                "summary": response[:500]
            }
            
        except Exception as e:
            logger.error(f"Error with HuggingFace analysis: {e}")
            return GroqAnalyzer()._fallback_analysis(data, query)


class GeminiAnalyzer:
    """Analyzer using Google Gemini API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = None
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini API initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
    
    def analyze(self, data: Dict[str, List[Dict[str, Any]]], query: str) -> Dict[str, Any]:
        """Analyze research data using Gemini."""
        if not self.model:
            logger.warning("Gemini model not available")
            return GroqAnalyzer()._fallback_analysis(data, query)
        
        try:
            context = GroqAnalyzer()._prepare_context(data)
            
            prompt = f"""Analyze the following research data about "{query}" and provide a comprehensive synthesis.

{context}

Provide:
1. Key Findings (3-5 main points)
2. Trends and Patterns
3. Notable Papers/Projects
4. Recommendations
5. Summary"""

            response = self.model.generate_content(prompt)
            
            return {
                "key_findings": [],
                "trends": response.text,
                "notable_items": [],
                "recommendations": [],
                "summary": response.text[:500]
            }
            
        except Exception as e:
            logger.error(f"Error with Gemini analysis: {e}")
            return GroqAnalyzer()._fallback_analysis(data, query)


class ResearchAnalyzer:
    """Main analyzer that tries multiple LLM providers."""
    
    def __init__(self):
        self.groq = GroqAnalyzer()
        self.huggingface = HuggingFaceAnalyzer()
        self.gemini = GeminiAnalyzer()
    
    def analyze(self, data: Dict[str, List[Dict[str, Any]]], query: str) -> Dict[str, Any]:
        """Analyze research data using available LLM provider."""
        
        # Try Groq first (best free tier)
        if self.groq.client:
            logger.info("Using Groq for analysis")
            return self.groq.analyze(data, query)
        
        # Try Gemini second
        if self.gemini.model:
            logger.info("Using Gemini for analysis")
            return self.gemini.analyze(data, query)
        
        # Try HuggingFace third
        if self.huggingface.client:
            logger.info("Using HuggingFace for analysis")
            return self.huggingface.analyze(data, query)
        
        # Fallback to rule-based analysis
        logger.warning("No LLM available, using fallback analysis")
        return self.groq._fallback_analysis(data, query)
