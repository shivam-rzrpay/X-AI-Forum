#!/usr/bin/env python3
"""
X AI-Forum Document Embedding Script

This script loads documents from the documents folder, splits them into chunks,
embeds them using Amazon Titan embeddings, and stores them in a ChromaDB vector database.
"""

import os
import logging
import boto3
from dotenv import load_dotenv
from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    PyPDFLoader, 
    Docx2txtLoader,
    UnstructuredMarkdownLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_aws import BedrockEmbeddings
from langchain_chroma import Chroma

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set paths
DOCUMENTS_PATH = os.path.join(os.path.dirname(__file__), "documents")
DB_PATH = os.path.join(os.path.dirname(__file__), "db")

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
AWS_PROFILE = os.getenv("AWS_PROFILE", "default")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.titan-embed-text-v2:0")

def load_documents():
    """Load documents from the documents directory."""
    logger.info(f"Loading documents from {DOCUMENTS_PATH}")
    
    # File type loaders
    loaders = {
        ".txt": DirectoryLoader(DOCUMENTS_PATH, glob="**/*.txt", loader_cls=TextLoader),
        ".pdf": DirectoryLoader(DOCUMENTS_PATH, glob="**/*.pdf", loader_cls=PyPDFLoader),
        ".docx": DirectoryLoader(DOCUMENTS_PATH, glob="**/*.docx", loader_cls=Docx2txtLoader),
        ".md": DirectoryLoader(DOCUMENTS_PATH, glob="**/*.md", loader_cls=UnstructuredMarkdownLoader)
    }
    
    all_documents = []
    for file_type, loader in loaders.items():
        try:
            logger.info(f"Loading {file_type} files...")
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} {file_type} documents")
            all_documents.extend(documents)
        except Exception as e:
            logger.error(f"Error loading {file_type} files: {e}")
    
    return all_documents

def split_documents(documents, chunk_size=500, chunk_overlap=50):
    """Split documents into chunks."""
    logger.info(f"Splitting documents into chunks of size {chunk_size} with overlap {chunk_overlap}")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Split into {len(chunks)} chunks")
    return chunks

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

def create_vector_store(chunks, embeddings):
    """Create a vector store from document chunks."""
    logger.info(f"Creating vector store at {DB_PATH}")
    
    # Check if DB directory exists, create if not
    if not os.path.exists(DB_PATH):
        os.makedirs(DB_PATH)
        logger.info(f"Created directory {DB_PATH}")
    
    # Create vector store
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_PATH
    )
    
    # No need to call persist() as it happens automatically with persist_directory
    logger.info(f"Vector store created and persisted to {DB_PATH}")
    
    return vector_store

def main():
    """Main function to load documents, create embeddings, and store them."""
    logger.info("Starting document embedding process")
    
    try:
        # Load documents
        documents = load_documents()
        if not documents:
            logger.error("No documents found. Please add documents to the documents directory.")
            return
        
        # Split documents into chunks
        chunks = split_documents(documents)
        
        # Create embeddings
        embeddings = create_embeddings()
        
        # Create vector store
        vector_store = create_vector_store(chunks, embeddings)
        
        logger.info(f"Successfully embedded {len(chunks)} document chunks into the vector store.")
        logger.info("Document embedding process completed successfully.")
    
    except Exception as e:
        logger.error(f"Error in document embedding process: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main() 