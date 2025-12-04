"""
Knowledge Base implementation using RAG (Retrieval-Augmented Generation).
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from ..config import RAGConfig, get_config

logger = logging.getLogger(__name__)


class Document:
    """Represents a document in the knowledge base."""
    
    def __init__(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.content = content
        self.metadata = metadata or {}
        self.id = None  # Set by the vector store
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary."""
        return {
            "content": self.content,
            "metadata": self.metadata
        }


class KnowledgeBase:
    """Manages the knowledge base with vector search capabilities."""
    
    def __init__(self, config: Optional[RAGConfig] = None):
        """Initialize the knowledge base."""
        if config is None:
            config = get_config().rag
        
        self.config = config
        self.vector_store = None
        self.embedding_model = None
        self.documents: List[Document] = []
        
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the vector store and embedding model."""
        logger.info("Initializing knowledge base...")
        
        # Load embedding model
        self._load_embedding_model()
        
        # Initialize vector store
        if self.config.vector_db_type == "chromadb":
            self._initialize_chromadb()
        elif self.config.vector_db_type == "faiss":
            self._initialize_faiss()
        else:
            raise ValueError(f"Unsupported vector DB type: {self.config.vector_db_type}")
    
    def _load_embedding_model(self) -> None:
        """Load the embedding model."""
        try:
            from sentence_transformers import SentenceTransformer
            
            logger.info(f"Loading embedding model: {self.config.embedding_model}")
            self.embedding_model = SentenceTransformer(self.config.embedding_model)
            logger.info("Embedding model loaded successfully")
        
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
    
    def _initialize_chromadb(self) -> None:
        """Initialize ChromaDB vector store."""
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Create persistent client
            db_path = Path(self.config.vector_db_path)
            db_path.mkdir(parents=True, exist_ok=True)
            
            client = chromadb.PersistentClient(
                path=str(db_path),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.vector_store = client.get_or_create_collection(
                name="knowledge_base",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"ChromaDB initialized at {db_path}")
        
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            raise
    
    def _initialize_faiss(self) -> None:
        """Initialize FAISS vector store."""
        try:
            import faiss
            import numpy as np
            
            # Get embedding dimension
            sample_embedding = self.embedding_model.encode(["test"])
            dimension = sample_embedding.shape[1]
            
            # Create FAISS index
            self.vector_store = faiss.IndexFlatL2(dimension)
            
            # Try to load existing index
            db_path = Path(self.config.vector_db_path)
            db_path.mkdir(parents=True, exist_ok=True)
            index_path = db_path / "faiss.index"
            
            if index_path.exists():
                self.vector_store = faiss.read_index(str(index_path))
                logger.info(f"Loaded existing FAISS index from {index_path}")
            else:
                logger.info("Created new FAISS index")
        
        except Exception as e:
            logger.error(f"Error initializing FAISS: {e}")
            raise
    
    def add_document(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a single document to the knowledge base."""
        return self.add_documents([content], [metadata] if metadata else None)[0]
    
    def add_documents(
        self,
        contents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """Add multiple documents to the knowledge base."""
        if not contents:
            return []
        
        if metadatas is None:
            metadatas = [{}] * len(contents)
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(contents)
        
        # Add to vector store
        if self.config.vector_db_type == "chromadb":
            return self._add_to_chromadb(contents, embeddings, metadatas)
        elif self.config.vector_db_type == "faiss":
            return self._add_to_faiss(contents, embeddings, metadatas)
    
    def _add_to_chromadb(
        self,
        contents: List[str],
        embeddings: Any,
        metadatas: List[Dict[str, Any]]
    ) -> List[str]:
        """Add documents to ChromaDB."""
        import uuid
        
        ids = [str(uuid.uuid4()) for _ in contents]
        
        self.vector_store.add(
            documents=contents,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(contents)} documents to ChromaDB")
        return ids
    
    def _add_to_faiss(
        self,
        contents: List[str],
        embeddings: Any,
        metadatas: List[Dict[str, Any]]
    ) -> List[str]:
        """Add documents to FAISS."""
        import uuid
        
        # Add embeddings to index
        self.vector_store.add(embeddings)
        
        # Store documents and metadata separately
        ids = [str(uuid.uuid4()) for _ in contents]
        for content, metadata, doc_id in zip(contents, metadatas, ids):
            doc = Document(content, metadata)
            doc.id = doc_id
            self.documents.append(doc)
        
        # Save index
        self._save_faiss_index()
        
        logger.info(f"Added {len(contents)} documents to FAISS")
        return ids
    
    def _save_faiss_index(self) -> None:
        """Save FAISS index to disk."""
        import faiss
        
        db_path = Path(self.config.vector_db_path)
        index_path = db_path / "faiss.index"
        docs_path = db_path / "documents.json"
        
        faiss.write_index(self.vector_store, str(index_path))
        
        # Save documents
        with open(docs_path, 'w') as f:
            json.dump([doc.to_dict() for doc in self.documents], f)
    
    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for relevant documents."""
        if top_k is None:
            top_k = self.config.top_k_results
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Search in vector store
        if self.config.vector_db_type == "chromadb":
            return self._search_chromadb(query_embedding, top_k, filter_metadata)
        elif self.config.vector_db_type == "faiss":
            return self._search_faiss(query_embedding, top_k)
    
    def _search_chromadb(
        self,
        query_embedding: Any,
        top_k: int,
        filter_metadata: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Search in ChromaDB."""
        results = self.vector_store.query(
            query_embeddings=query_embedding.tolist(),
            n_results=top_k,
            where=filter_metadata
        )
        
        documents = []
        for i in range(len(results['documents'][0])):
            doc = {
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i],
                'id': results['ids'][0][i]
            }
            documents.append(doc)
        
        return documents
    
    def _search_faiss(
        self,
        query_embedding: Any,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Search in FAISS."""
        distances, indices = self.vector_store.search(query_embedding, top_k)
        
        documents = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx]
                documents.append({
                    'content': doc.content,
                    'metadata': doc.metadata,
                    'distance': float(distances[0][i]),
                    'id': doc.id
                })
        
        return documents
    
    def get_context(self, query: str, max_length: int = 2000) -> str:
        """Get context for a query by retrieving relevant documents."""
        results = self.search(query)
        
        context_parts = []
        total_length = 0
        
        for result in results:
            content = result['content']
            if total_length + len(content) > max_length:
                break
            context_parts.append(content)
            total_length += len(content)
        
        return "\n\n".join(context_parts)
    
    def clear(self) -> None:
        """Clear all documents from the knowledge base."""
        try:
            if self.config.vector_db_type == "chromadb":
                # ChromaDB: delete the collection and recreate it
                import chromadb
                client = chromadb.PersistentClient(path=self.config.vector_db_path)
                try:
                    client.delete_collection(name="knowledge_base")
                except Exception:
                    pass  # Collection might not exist
                self._initialize_chromadb()
            elif self.config.vector_db_type == "faiss":
                self._initialize_faiss()
                self.documents = []
            
            logger.info("Knowledge base cleared")
        except Exception as e:
            logger.error(f"Error clearing knowledge base: {e}")
            raise
