import os
import logging
import numpy as np
import json
import time

# Check if chromadb is available
try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("chromadb not available. Using fallback memory storage.")

class SelfLearningAI:
    """
    Implements real-time learning and memory capabilities.
    Stores conversation history and context using vector embeddings.
    """
    
    def __init__(self, collection_name="ai_memory", persist_directory="memory_db"):
        """
        Initialize the self-learning module.
        
        Args:
            collection_name (str): Name of the memory collection
            persist_directory (str): Directory to persist memory
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        # Create directory if it doesn't exist
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize memory database
        self.client = None
        self.collection = None
        self.embedding_function = None
        
        if CHROMADB_AVAILABLE:
            try:
                # Initialize ChromaDB client
                self.client = chromadb.PersistentClient(path=self.persist_directory)
                
                # Initialize embedding function - use sentence transformers if available
                try:
                    self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                        model_name="all-MiniLM-L6-v2"
                    )
                except:
                    # Fallback to default embedding
                    self.embedding_function = None
                
                # Get or create collection
                self.collection = self.client.get_or_create_collection(
                    name=self.collection_name,
                    embedding_function=self.embedding_function
                )
                
                logging.info(f"Initialized ChromaDB memory with collection: {collection_name}")
            except Exception as e:
                logging.error(f"Error initializing ChromaDB: {e}")
                self.client = None
                self.collection = None
        
        # Fallback memory if ChromaDB is not available
        if not CHROMADB_AVAILABLE or not self.collection:
            self.fallback_memory = []
            self.fallback_memory_file = os.path.join(self.persist_directory, "memory.json")
            self._load_fallback_memory()
            logging.info("Using fallback memory storage")
    
    def _load_fallback_memory(self):
        """Load memory from fallback file storage."""
        if os.path.exists(self.fallback_memory_file):
            try:
                with open(self.fallback_memory_file, 'r') as f:
                    self.fallback_memory = json.load(f)
            except Exception as e:
                logging.error(f"Error loading fallback memory: {e}")
                self.fallback_memory = []
    
    def _save_fallback_memory(self):
        """Save memory to fallback file storage."""
        try:
            with open(self.fallback_memory_file, 'w') as f:
                json.dump(self.fallback_memory, f)
        except Exception as e:
            logging.error(f"Error saving fallback memory: {e}")
    
    def generate_embedding(self, text):
        """
        Generate an embedding vector for the text.
        Creates a basic embedding if advanced methods unavailable.
        
        Args:
            text (str): Text to embed
            
        Returns:
            list: Embedding vector
        """
        if not text:
            # Return zero vector for empty text
            return [0.0] * 768
        
        # If using ChromaDB with embedding function, it will handle this internally
        if not self.embedding_function:
            # Create a deterministic embedding based on text hash
            # This is a very simple fallback that won't have semantic properties
            np.random.seed(hash(text) % 2**32)
            return list(np.random.normal(0, 1, 768).astype(float))
    
    def store_interaction(self, query, response):
        """
        Store a conversation interaction in memory.
        
        Args:
            query (str): User query
            response (str): AI response
            
        Returns:
            bool: Success status
        """
        if not query or not response:
            return False
        
        # Create unique ID using timestamp and query hash
        interaction_id = f"{time.time()}_{hash(query) % 10000}"
        document = f"Query: {query}\nResponse: {response}"
        metadata = {
            "type": "interaction",
            "timestamp": time.time(),
            "query": query
        }
        
        # Store in ChromaDB if available
        if CHROMADB_AVAILABLE and self.collection:
            try:
                self.collection.add(
                    ids=[interaction_id],
                    documents=[document],
                    metadatas=[metadata]
                )
                logging.info(f"Stored interaction in ChromaDB: {interaction_id}")
                return True
            except Exception as e:
                logging.error(f"Error storing in ChromaDB: {e}")
                # Fall through to fallback
        
        # Fallback storage
        try:
            self.fallback_memory.append({
                "id": interaction_id,
                "document": document,
                "metadata": metadata,
                "embedding": self.generate_embedding(query)
            })
            self._save_fallback_memory()
            logging.info(f"Stored interaction in fallback memory: {interaction_id}")
            return True
        except Exception as e:
            logging.error(f"Error storing in fallback memory: {e}")
            return False
    
    def retrieve_context(self, query, top_k=3):
        """
        Retrieve relevant context for a query.
        
        Args:
            query (str): Query to find context for
            top_k (int): Number of relevant items to retrieve
            
        Returns:
            str: Retrieved context as concatenated text
        """
        if not query:
            return ""
        
        # Retrieve from ChromaDB if available
        if CHROMADB_AVAILABLE and self.collection:
            try:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=top_k
                )
                
                if results and 'documents' in results and results['documents']:
                    documents = results['documents'][0]
                    if documents:
                        return "\n\n".join(documents)
            except Exception as e:
                logging.error(f"Error retrieving from ChromaDB: {e}")
                # Fall through to fallback
        
        # Fallback retrieval - basic text matching
        if self.fallback_memory:
            try:
                # Extremely simple matching - just look for word overlap
                query_words = set(query.lower().split())
                
                # Calculate a basic relevance score for each memory item
                scored_items = []
                for item in self.fallback_memory:
                    doc_words = set(item["document"].lower().split())
                    overlap = len(query_words.intersection(doc_words))
                    scored_items.append((overlap, item))
                
                # Sort by score and take top k
                scored_items.sort(reverse=True, key=lambda x: x[0])
                top_items = [item for _, item in scored_items[:top_k]]
                
                if top_items:
                    return "\n\n".join([item["document"] for item in top_items])
            except Exception as e:
                logging.error(f"Error retrieving from fallback memory: {e}")
        
        return ""
    
    def get_combined_context(self, query):
        """
        Get context enhanced query for better responses.
        
        Args:
            query (str): Original query
            
        Returns:
            str: Query enhanced with context
        """
        context = self.retrieve_context(query)
        if context:
            return f"Based on previous interactions:\n{context}\n\nCurrent query: {query}"
        return query
    
    def clear_memory(self):
        """
        Clear all stored memory.
        
        Returns:
            bool: Success status
        """
        # Clear ChromaDB if available
        if CHROMADB_AVAILABLE and self.collection:
            try:
                self.collection.delete(where={})
                logging.info("Cleared ChromaDB memory")
            except Exception as e:
                logging.error(f"Error clearing ChromaDB memory: {e}")
                return False
        
        # Clear fallback memory
        self.fallback_memory = []
        self._save_fallback_memory()
        logging.info("Cleared fallback memory")
        
        return True
    
    def get_memory_stats(self):
        """
        Get statistics about stored memory.
        
        Returns:
            dict: Memory statistics
        """
        stats = {
            "backend": "ChromaDB" if CHROMADB_AVAILABLE and self.collection else "Fallback",
            "items_count": 0,
            "unique_queries": 0
        }
        
        if CHROMADB_AVAILABLE and self.collection:
            try:
                # Count items in ChromaDB
                collection_count = self.collection.count()
                stats["items_count"] = collection_count
                
                # Try to estimate unique queries
                if collection_count > 0:
                    results = self.collection.get(limit=1000)
                    if 'metadatas' in results and results['metadatas']:
                        unique_queries = set()
                        for metadata in results['metadatas']:
                            if 'query' in metadata:
                                unique_queries.add(metadata['query'])
                        stats["unique_queries"] = len(unique_queries)
            except Exception as e:
                logging.error(f"Error getting ChromaDB stats: {e}")
        else:
            # Stats from fallback memory
            stats["items_count"] = len(self.fallback_memory)
            stats["unique_queries"] = len(set([item["metadata"]["query"] for item in self.fallback_memory if "metadata" in item and "query" in item["metadata"]]))
        
        return stats