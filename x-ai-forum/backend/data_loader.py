import os
import json
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import embedding_utils as utils

# Sample data for bootstrapping the forum
SAMPLE_DATA = [
    {
        "forum": "General Discussion",
        "title": "Welcome to our Internal Forum",
        "author": "Admin",
        "content": """
Welcome to our new internal discussion forum!

This platform is designed to foster communication and knowledge sharing across our organization. 
Feel free to post questions, share insights, or start discussions on topics relevant to our work.

For technical issues, please use the Technical Support forum.
For product ideas, please use the Product Ideas forum.
For HR and benefits questions, please use the HR & Benefits forum.

Let's build a collaborative community together!
        """
    },
    {
        "forum": "Technical Support",
        "title": "AWS Bedrock Setup Guide",
        "author": "Cloud Team",
        "content": """
# AWS Bedrock Setup Guide

Here's a step-by-step guide to setting up AWS Bedrock for your projects:

1. Log in to AWS Console and navigate to Bedrock
2. Request model access for:
   - Anthropic Claude models
   - Amazon Titan models
3. Set up authentication:
   - Create an IAM role with Bedrock permissions
   - Configure AWS CLI with appropriate credentials
4. Start using models via:
   - AWS Console
   - API calls with SDK
   - Integration with LangChain

For any issues, please contact the Cloud Team.
        """
    },
    {
        "forum": "Product Ideas",
        "title": "AI-powered customer service chatbot",
        "author": "Innovation Team",
        "content": """
# AI-powered Customer Service Chatbot

I propose we develop an AI-powered customer service chatbot using Claude 3 to improve response times and reduce support costs.

Key benefits:
- 24/7 availability
- Consistent responses
- Lower support costs
- Reduced wait times for customers

Technical implementation:
1. Use AWS Bedrock with Claude 3
2. Integrate with our existing customer support system
3. Train on our product documentation and past support conversations
4. Implement a fallback mechanism for complex queries

What do you think? Would this provide value to our customers?
        """
    },
    {
        "forum": "HR & Benefits",
        "title": "Health Insurance Open Enrollment",
        "author": "HR Team",
        "content": """
# Health Insurance Open Enrollment Period 2025

Important dates:
- Open enrollment begins: November 1, 2024
- Open enrollment ends: November 30, 2024
- Coverage effective: January 1, 2025

Changes this year:
- New PPO option with lower deductibles
- Enhanced mental health coverage
- Telehealth visits with $0 copay
- Expanded dental provider network

Information sessions:
- November 5, 10:00 AM - Main Conference Room
- November 12, 2:00 PM - Virtual Meeting (Zoom link to be shared)
- November 20, 3:30 PM - Main Conference Room

Please review all plan options carefully. For questions, contact HR at benefits@company.com.
        """
    }
]

def convert_to_documents(data):
    """Convert sample data to LangChain documents."""
    documents = []
    
    for item in data:
        doc = Document(
            page_content=item["content"],
            metadata={
                "forum": item["forum"],
                "title": item["title"],
                "author": item["author"]
            }
        )
        documents.append(doc)
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    
    split_docs = text_splitter.split_documents(documents)
    return split_docs

def create_sample_db():
    """Create a sample vector database using mock data."""
    # Convert sample data to documents
    documents = convert_to_documents(SAMPLE_DATA)
    
    # Create vector database
    db_path = os.path.join(os.path.dirname(__file__), "vector_db")
    vector_db = utils.create_vector_db(documents, db_path)
    
    print(f"Created vector database at {db_path} with {len(documents)} documents")
    return vector_db

if __name__ == "__main__":
    # Create the sample database when run directly
    create_sample_db() 