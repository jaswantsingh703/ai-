import os
import logging
import numpy as np

# Check if chromadb is available
try:
    from chromadb import Client
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("chromadb module not available. Memory functionality will be limited.")

class SelfLearningAI:
    """
    Real-time learning module that stores and retrieves conversation interactions.
    """
    
    def __init__(self, persist_directory="memory_db", collection_name="ai_memory"):
        """
        Initialize the self-learning AI with memory storage.
        
        Args:
            persist_directory (str): Directory to store memory database
            collection_name (str): Name of the memory collection
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.collection = None
        
        # Create persist directory if it doesn't exist
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize ChromaDB if available
        if CHROMADB_AVAILABLE:
            try:
                self.client = Client(Settings(
                    chroma_db_impl="duckdb+parquet",
                    persist_directory=self.persist_directory
                ))
                self.collection = self.client.get_or_create_collection(name=collection_name)
                logging.info(f"SelfLearningAI initialized with collection: {collection_name}")
            except Exception as e:
                logging.error(f"Error initializing ChromaDB: {e}")
                self.client = None
        else:
            logging.warning("ChromaDB not available. Using fallback memory storage.")
            self.memory_store = []
    
    def generate_embedding(self, text):
        """
        Generates a dummy 768-dimensional embedding for the given text.
        In production, replace with a real embedding model.
        
        Args:
            text (str): Text to generate embedding for
            
        Returns:
            list: 768-dimensional embedding vector
        """
        # Use text hash as seed for reproducibility
        seed = hash(text) % (2**32)
        np.random.seed(seed)
        embedding = np.random.rand(768).tolist()  # Dummy 768-dim vector
        return embedding
    
    def store_interaction(self, query, response):
        """
        Stores a conversation interaction (query and response) into the memory.
        
        Args:
            query (str): User query
            response (str): AI response
            
        Returns:
            bool: Success status
        """
        if not query or not response:
            return False
            
        try:
            # Create a unique ID for the interaction (hash of query)
            doc_id = str(hash(query))
            document = f"Query: {query}\nResponse: {response}"
            
            if CHROMADB_AVAILABLE and self.collection:
                # Store in ChromaDB
                embedding = self.generate_embedding(query)
                self.collection.add(
                    documents=[document],
                    embeddings=[embedding],
                    ids=[doc_id]
                )
                logging.info(f"Stored interaction with id: {doc_id}")
                return True
            else:
                # Fallback to simple list storage
                self.memory_store.append({
                    "id": doc_id,
                    "query": query,
                    "response": response
                })
                logging.info(f"Stored interaction in fallback memory: {doc_id}")
                return True
        except Exception as e:
            logging.error(f"Error storing interaction: {e}")
            return False
    
    def retrieve_context(self, query, top_k=3):
        """
        Retrieves similar interactions for the given query.
        
        Args:
            query (str): Query to find similar interactions for
            top_k (int): Number of similar interactions to retrieve
            
        Returns:
            str: Retrieved context as concatenated text
        """
        if not query:
            return ""
            
        try:
            if CHROMADB_AVAILABLE and self.collection:
                # Retrieve from ChromaDB
                embedding = self.generate_embedding(query)
                results = self.collection.query(
                    query_embeddings=[embedding],
                    n_results=top_k,
                    include=["documents"]
                )
                documents = results.get("documents", [[]])[0]
                context = "\n\n".join(documents)
                logging.info(f"Retrieved context for query: {query}")
                return context
            else:
                # Simple exact match from fallback memory
                matching = [item for item in self.memory_store if query.lower() in item["query"].lower()]
                matching = matching[:top_k]
                context = "\n\n".join([f"Query: {item['query']}\nResponse: {item['response']}" for item in matching])
                return context
        except Exception as e:
            logging.error(f"Error retrieving context: {e}")
            return ""
    
    def get_combined_context(self, query):
        """
        Retrieves the stored context for a query.
        Can be used to augment the AI model's input.
        
        Args:
            query (str): Query to find context for
            
        Returns:
            str: Combined context
        """
        context = self.retrieve_context(query)
        if context:
            return f"Previous relevant interactions:\n{context}\n\nCurrent query: {query}"
        return query
    
    def clear_memory(self):
        """
        Clears all stored memory.
        
        Returns:
            bool: Success status
        """
        try:
            if CHROMADB_AVAILABLE and self.collection:
                # Clear ChromaDB collection
                self.collection.delete(where={})
                logging.info("Cleared memory collection")
            else:
                # Clear fallback memory
                self.memory_store = []
                logging.info("Cleared fallback memory")
            return True
        except Exception as e:
            logging.error(f"Error clearing memory: {e}")
            return False