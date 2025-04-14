#!/usr/bin/env python3
"""
X AI-Forum Embeddings Test Script

This script tests the embeddings by performing a simple similarity search 
on the vector database created by embed_docs.py.
"""

import os
import logging
import boto3
from dotenv import load_dotenv
from langchain_aws import BedrockEmbeddings
from langchain_chroma import Chroma

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set paths
DB_PATH = os.path.join(os.path.dirname(__file__), "db")

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
AWS_PROFILE = os.getenv("AWS_PROFILE", "default")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.titan-embed-text-v2:0")

def create_embeddings():
    """Create embeddings using Amazon Bedrock Titan."""
    logger.info(f"Creating AWS Bedrock session with profile {AWS_PROFILE} in region {AWS_REGION}")
    
    try:
        # Create AWS session
        session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
        
        # Create Bedrock client
        bedrock_client = session.client('bedrock-runtime')
        
        # Initialize embeddings
        embeddings = BedrockEmbeddings(
            client=bedrock_client,
            model_id=BEDROCK_MODEL_ID,
        )
        
        logger.info(f"Initialized embeddings with model {BEDROCK_MODEL_ID}")
        return embeddings
    except Exception as e:
        logger.error(f"Error creating embeddings: {e}")
        raise

def test_similarity_search(query):
    """Test similarity search on the vector store."""
    try:
        # Check if DB exists
        if not os.path.exists(DB_PATH):
            logger.error(f"Vector database not found at {DB_PATH}. Run embed_docs.py first.")
            return
        
        # Create embeddings
        embeddings = create_embeddings()
        
        # Load vector store
        vector_store = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
        
        # Perform similarity search
        logger.info(f"Performing similarity search for query: '{query}'")
        results = vector_store.similarity_search(query, k=3)
        
        # Print results
        logger.info(f"Search Results for: '{query}'")
        logger.info("-" * 50)
        for i, doc in enumerate(results):
            logger.info(f"Result {i+1}:")
            logger.info(f"Source: {doc.metadata.get('source', 'Unknown')}")
            logger.info(f"Content: {doc.page_content[:200]}...")
            logger.info("-" * 50)
            
        return results
    
    except Exception as e:
        logger.error(f"Error in similarity search: {e}")
        import traceback
        logger.error(traceback.format_exc())

def main():
    """Main function to test the vector store."""
    logger.info("Testing vector embeddings and similarity search")
    
    # Test queries
    test_queries = [
        "What is AWS Bedrock?",
        "How do vector embeddings work?",
        "Tell me about Slack bots and their features"
    ]
    
    for query in test_queries:
        test_similarity_search(query)
        print()  # Add space between queries
    
    logger.info("Embedding test completed")

if __name__ == "__main__":
    main() 