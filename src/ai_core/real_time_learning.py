# Python script
import os
import logging
import numpy as np
from chromadb import Client
from chromadb.config import Settings

# Configure logging
logging.basicConfig(
    filename="logs/real_time_learning.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class SelfLearningAI:
    """
    This class implements real-time learning for the AI Assistant.
    It stores conversation interactions in a memory collection using ChromaDB
    and retrieves similar contexts based on a generated embedding.
    
    For production use, replace the dummy embedding generator with a real one
    (e.g., using OpenAI embeddings or sentence-transformers).
    """
    
    def __init__(self, persist_directory="memory_db", collection_name="ai_memory"):
        self.persist_directory = persist_directory
        # Initialize ChromaDB client with persistence support.
        self.client = Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=self.persist_directory
        ))
        # Get or create the memory collection.
        self.collection = self.client.get_or_create_collection(name=collection_name)
        logging.info("SelfLearningAI initialized with collection: %s", collection_name)
    
    def generate_embedding(self, text):
        """
        Generates a dummy 768-dimensional embedding for the given text.
        Replace this function with a call to a real embedding model in production.
        """
        # Use text hash as seed for reproducibility.
        seed = hash(text) % (2**32)
        np.random.seed(seed)
        embedding = np.random.rand(768).tolist()  # Dummy 768-dim vector.
        return embedding
    
    def store_interaction(self, query, response):
        """
        Stores a conversation interaction (query and response) into the memory.
        """
        embedding = self.generate_embedding(query)
        # Create a unique ID for the interaction (here using hash of query).
        doc_id = str(hash(query))
        document = f"Query: {query}\nResponse: {response}"
        self.collection.add(
            documents=[document],
            embeddings=[embedding],
            ids=[doc_id]
        )
        logging.info("Stored interaction with id: %s", doc_id)
    
    def retrieve_context(self, query, top_k=3):
        """
        Retrieves the top_k similar interactions (context) for the given query.
        Returns the concatenated documents as a string.
        """
        embedding = self.generate_embedding(query)
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            include=["documents"]
        )
        # Get the list of documents from the query results.
        documents = results.get("documents", [[]])[0]
        context = "\n".join(documents)
        logging.info("Retrieved context for query: %s", query)
        return context
    
    def update_model(self, training_data):
        """
        Placeholder for model update/fine-tuning with new training data.
        In production, integrate this method with your fine-tuning pipeline.
        """
        logging.info("Updating model with training data: %s", training_data)
        # Here, you would trigger your model update/fine-tuning process.
        print("Model updated with new training data.")
        return True
    
    def get_combined_context(self, query):
        """
        Retrieves the stored context for a query.
        Can be used to augment the AI model's input.
        """
        context = self.retrieve_context(query)
        return context

# Example usage for testing the self-learning functionality
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize the self-learning module
    self_learning = SelfLearningAI()
    
    # Example interaction: store a query-response pair
    query1 = "What is the capital of France?"
    response1 = "The capital of France is Paris."
    self_learning.store_interaction(query1, response1)
    
    # Retrieve context for a similar query
    new_query = "Tell me the capital of France."
    context = self_learning.retrieve_context(new_query)
    print("Retrieved Context:")
    print(context)
    
    # Simulate a model update with dummy training data
    training_data = [
        {"input": query1, "output": response1},
        {"input": new_query, "output": "Paris is the capital of France."}
    ]
    self_learning.update_model(training_data)