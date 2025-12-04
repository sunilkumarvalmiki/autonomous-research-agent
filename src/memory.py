"""
Memory and caching module for agent persistence and learning.
Uses vector database for semantic search and caching.
"""

import os
import json
import logging
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorMemory:
    """Vector-based memory for semantic search and caching."""
    
    def __init__(self, persist_directory: str = "./agent_memory"):
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        
        try:
            import chromadb
            from chromadb.config import Settings
            
            self.client = chromadb.Client(Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False
            ))
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="research_memory",
                metadata={"description": "Semantic memory of past research"}
            )
            
            logger.info("Vector memory initialized successfully")
        except ImportError:
            logger.warning("chromadb not available, vector memory disabled")
        except Exception as e:
            logger.error(f"Failed to initialize vector memory: {e}")
    
    def store_research(self, query: str, data: Dict[str, Any], analysis: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """Store a research result in memory."""
        if not self.collection:
            return
        
        try:
            # Create a document from the research
            doc_id = hashlib.md5(query.encode()).hexdigest()
            
            document = {
                "query": query,
                "summary": analysis.get("summary", ""),
                "key_findings": analysis.get("key_findings", []),
                "timestamp": datetime.now().isoformat(),
                "data_count": {k: len(v) for k, v in data.items()},
                "metadata": metadata or {}
            }
            
            # Create embedding text
            embedding_text = f"{query}\n{analysis.get('summary', '')}\n" + "\n".join(analysis.get('key_findings', []))
            
            self.collection.add(
                documents=[embedding_text],
                metadatas=[document],
                ids=[doc_id]
            )
            
            logger.info(f"Stored research in memory: {query}")
        except Exception as e:
            logger.error(f"Failed to store research: {e}")
    
    def search_similar(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar past research."""
        if not self.collection:
            return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            if results and results['metadatas']:
                similar_research = results['metadatas'][0]
                logger.info(f"Found {len(similar_research)} similar past researches")
                return similar_research
            
            return []
        except Exception as e:
            logger.error(f"Failed to search memory: {e}")
            return []
    
    def get_recent_research(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent research entries."""
        if not self.collection:
            return []
        
        try:
            # Get all items and sort by timestamp
            all_items = self.collection.get()
            
            if all_items and all_items['metadatas']:
                metadatas = all_items['metadatas']
                # Sort by timestamp (most recent first)
                sorted_items = sorted(
                    metadatas,
                    key=lambda x: x.get('timestamp', ''),
                    reverse=True
                )
                return sorted_items[:limit]
            
            return []
        except Exception as e:
            logger.error(f"Failed to get recent research: {e}")
            return []


class CacheManager:
    """Manages caching for expensive operations."""
    
    def __init__(self, cache_dir: str = "./cache", ttl_hours: int = 24):
        self.cache_dir = cache_dir
        self.ttl = timedelta(hours=ttl_hours)
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, key: str) -> str:
        """Generate cache file path."""
        cache_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if exists and not expired."""
        cache_file = self._get_cache_key(key)
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            # Check expiration
            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                logger.info(f"Cache expired for key: {key[:50]}...")
                os.remove(cache_file)
                return None
            
            logger.info(f"Cache hit for key: {key[:50]}...")
            return cached_data['value']
        except Exception as e:
            logger.error(f"Error reading cache: {e}")
            return None
    
    def set(self, key: str, value: Any):
        """Set cache value."""
        cache_file = self._get_cache_key(key)
        
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'key': key,
                'value': value
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
            
            logger.info(f"Cached value for key: {key[:50]}...")
        except Exception as e:
            logger.error(f"Error writing cache: {e}")
    
    def clear(self):
        """Clear all cache files."""
        for file in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, file)
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Error removing cache file: {e}")
        
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
        
        total_size = 0
        valid_count = 0
        expired_count = 0
        
        for file in cache_files:
            file_path = os.path.join(self.cache_dir, file)
            total_size += os.path.getsize(file_path)
            
            try:
                with open(file_path, 'r') as f:
                    cached_data = json.load(f)
                
                cached_time = datetime.fromisoformat(cached_data['timestamp'])
                if datetime.now() - cached_time > self.ttl:
                    expired_count += 1
                else:
                    valid_count += 1
            except (OSError, json.JSONDecodeError, KeyError) as e:
                # Ignore files that cannot be read or parsed; they are not counted as valid/expired.
                logger.warning(f"Skipping cache file '{file_path}' due to error: {e}")
        
        return {
            'total_files': len(cache_files),
            'valid_count': valid_count,
            'expired_count': expired_count,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }


class AgentMemory:
    """Combined memory system for the agent."""
    
    def __init__(self, enable_vector_memory: bool = True, enable_cache: bool = True):
        self.vector_memory = VectorMemory() if enable_vector_memory else None
        self.cache = CacheManager() if enable_cache else None
        self.session_history = []
    
    def remember_research(self, query: str, data: Dict[str, Any], analysis: Dict[str, Any]):
        """Store research in long-term memory."""
        if self.vector_memory:
            self.vector_memory.store_research(query, data, analysis)
        
        # Also add to session history
        self.session_history.append({
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'data_count': sum(len(v) for v in data.values()),
            'summary': analysis.get('summary', '')[:200]
        })
    
    def recall_similar(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Recall similar past research."""
        if self.vector_memory:
            return self.vector_memory.search_similar(query, limit)
        return []
    
    def get_context_from_memory(self, query: str) -> str:
        """Get relevant context from memory for the current query."""
        similar = self.recall_similar(query, limit=3)
        
        if not similar:
            return ""
        
        context = "## Relevant Past Research:\n\n"
        for i, research in enumerate(similar, 1):
            context += f"{i}. **{research.get('query', 'Unknown')}** "
            context += f"({research.get('timestamp', 'Unknown date')})\n"
            context += f"   Summary: {research.get('summary', 'N/A')[:150]}...\n\n"
        
        return context
