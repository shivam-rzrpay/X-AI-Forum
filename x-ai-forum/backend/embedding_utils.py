import boto3
import json
import os
from dotenv import load_dotenv
import numpy as np
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.document_loaders import TextLoader

# Load environment variables
load_dotenv()

# Configure AWS Bedrock
def get_bedrock_client():
    """Get an AWS Bedrock client."""
    session = boto3.Session(profile_name=os.getenv('AWS_PROFILE'))
    return session.client('bedrock-runtime', region_name=os.getenv('AWS_REGION', 'ap-south-1'))

def get_embedding(text):
    """Get embedding for a text using AWS Bedrock Titan Embeddings."""
    client = get_bedrock_client()
    
    # Use Amazon Titan Embeddings model
    model_id = "amazon.titan-embed-text-v2:0"
    
    # Prepare the request body
    request_body = {
        "inputText": text,
        "embeddingConfig": {
            "outputEmbeddingLength": 1536  # Standard embedding size
        }
    }
    
    # Call the Bedrock model
    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps(request_body)
    )
    
    # Parse the response
    response_body = json.loads(response.get('body').read())
    embedding = response_body.get('embedding')
    
    return embedding

def create_vector_db(documents, db_path="./vector_db"):
    """Create a ChromaDB vector database from documents."""
    # Initialize Bedrock embeddings
    bedrock_embeddings = BedrockEmbeddings(
        client=get_bedrock_client(),
        model_id="amazon.titan-embed-text-v2:0"
    )
    
    # Create Chroma vector store
    vector_db = Chroma.from_documents(
        documents=documents,
        embedding=bedrock_embeddings,
        persist_directory=db_path
    )
    
    # Persist the vector store
    vector_db.persist()
    
    return vector_db

def load_vector_db(db_path="./vector_db"):
    """Load an existing ChromaDB vector database."""
    # Initialize Bedrock embeddings
    bedrock_embeddings = BedrockEmbeddings(
        client=get_bedrock_client(),
        model_id="amazon.titan-embed-text-v2:0"
    )
    
    # Load Chroma vector store
    vector_db = Chroma(
        persist_directory=db_path,
        embedding_function=bedrock_embeddings
    )
    
    return vector_db

def semantic_search(query, vector_db, top_k=5):
    """Perform semantic search using the vector database."""
    # Search for similar documents
    results = vector_db.similarity_search_with_score(query, k=top_k)
    
    # Format the results
    formatted_results = []
    for doc, score in results:
        formatted_results.append({
            "content": doc.page_content,
            "metadata": doc.metadata,
            "score": float(score)  # Convert from numpy float to Python float for JSON serialization
        })
    
    return formatted_results 