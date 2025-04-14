from flask import Flask, request, jsonify, Response, session, redirect, url_for
import boto3
import json
import os
import threading
import logging
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
import embedding_utils as utils
import data_loader
from flask_cors import CORS
import slack_integration
from langchain_aws import BedrockEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
import secrets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24).hex())
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
CORS(app, supports_credentials=True)  # Enable CORS with credentials support

# Store user info
users = {}

# Configure AWS Bedrock
session_aws = boto3.Session(profile_name=os.getenv('AWS_PROFILE'))
bedrock_client = session_aws.client('bedrock-runtime', region_name=os.getenv('AWS_REGION'))

# Model IDs
EMBEDDING_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'amazon.titan-embed-text-v2:0')  # For embeddings
CHAT_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"  # For chat/conversation

logger.info(f"Using embedding model: {EMBEDDING_MODEL_ID}")
logger.info(f"Using chat model: {CHAT_MODEL_ID}")

# Store chat histories - using a dictionary with session IDs as keys
chat_histories = {}

# Initialize vector database
vector_db = None
try:
    db_path = os.path.join(os.path.dirname(__file__), "db")
    if os.path.exists(db_path):
        # Initialize embeddings
        embeddings = BedrockEmbeddings(
            client=bedrock_client,
            model_id=EMBEDDING_MODEL_ID,
        )
        
        # Load the vector store
        vector_db = Chroma(persist_directory=db_path, embedding_function=embeddings)
        logger.info(f"Loaded vector database from {db_path}")
    else:
        # Fall back to sample database if needed
        vector_db = data_loader.create_sample_db()
        logger.info(f"Vector database not found at {db_path}, using sample data")
except Exception as e:
    logger.error(f"Error initializing vector database: {str(e)}")
    # Create sample database as fallback
    vector_db = data_loader.create_sample_db()
    logger.info("Using sample database as fallback due to initialization error")

# Authentication routes
@app.route('/login')
def login():
    """Redirect to Google login page."""
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    """Handle the OAuth 2.0 callback from Google."""
    try:
        token = google.authorize_access_token()
        resp = google.get('userinfo')
        user_info = resp.json()
        
        # Store user info
        user_id = user_info['email']
        users[user_id] = {
            'email': user_info['email'],
            'name': user_info.get('name', 'User'),
            'picture': user_info.get('picture', ''),
            'last_login': datetime.now().isoformat()
        }
        
        # Set session info
        session['user_id'] = user_id
        session['logged_in'] = True
        
        # Generate an API token for the frontend
        api_token = secrets.token_hex(16)
        users[user_id]['api_token'] = api_token
        
        # Redirect to frontend with token
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:8080')
        return redirect(f"{frontend_url}/?token={api_token}&user={user_id}")
    
    except Exception as e:
        logger.error(f"Authorization error: {str(e)}")
        return jsonify({"error": "Authorization failed"}), 401

@app.route('/user/me')
def get_user():
    """Get current user info."""
    # Check token from Authorization header
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        
        # Find user with matching token
        for user_id, user_data in users.items():
            if user_data.get('api_token') == token:
                return jsonify({
                    "user_id": user_id,
                    "email": user_data['email'],
                    "name": user_data['name'],
                    "picture": user_data['picture']
                })
    
    return jsonify({"error": "Unauthorized"}), 401

@app.route('/logout')
def logout():
    """Log out the current user."""
    session.pop('user_id', None)
    session.pop('logged_in', None)
    return jsonify({"status": "success", "message": "Logged out successfully"})

# Authentication middleware
def require_auth(view_function):
    def decorated_function(*args, **kwargs):
        # Check if user is logged in via session
        if session.get('logged_in'):
            return view_function(*args, **kwargs)
        
        # Check token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            # Validate token
            for user_id, user_data in users.items():
                if user_data.get('api_token') == token:
                    return view_function(*args, **kwargs)
        
        return jsonify({"error": "Unauthorized"}), 401
    
    # Preserve the original function name and docstring
    decorated_function.__name__ = view_function.__name__
    decorated_function.__doc__ = view_function.__doc__
    
    return decorated_function

def ask_claude(question, session_id=None):
    """Ask Claude a question and return the response, with context from chat history."""
    try:
        # Create or get chat history for this session
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        if session_id not in chat_histories:
            chat_histories[session_id] = []
        
        chat_history = chat_histories[session_id]
        
        # Check if we should use RAG with the vector database
        use_rag = vector_db is not None and len(question.strip()) > 0
        
        if use_rag:
            # Search for relevant content
            docs = vector_db.similarity_search(question, k=3)
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # System prompt with context
            system_prompt = [{"text": f"""You are a helpful forum assistant for a company's internal discussion forum. 
Answer questions clearly and concisely based on the following context information:

{context}

If the context doesn't contain the answer, you can use your general knowledge but make it clear when you're doing so."""}]
        else:
            # Standard system prompt
            system_prompt = [{"text": "You are a helpful forum assistant for a company's internal discussion forum. Answer questions clearly and concisely."}]
        
        # Build messages from chat history
        messages = []
        for entry in chat_history:
            if entry["role"] == "user":
                messages.append({
                    "role": "user",
                    "content": [{"text": entry["content"]}]
                })
            else:
                messages.append({
                    "role": "assistant",
                    "content": [{"text": entry["content"]}]
                })
        
        # Add the current question
        messages.append({
            "role": "user", 
            "content": [{"text": question}]
        })
        
        # Call Claude model (using the chat model ID, not the embedding model)
        response = bedrock_client.converse(
            modelId=CHAT_MODEL_ID,  # Use Claude for generation
            messages=messages,
            system=system_prompt,
            inferenceConfig={"temperature": 0.7, "topP": 0.9}
        )
        
        # Extract and format the response
        answer = ""
        for content in response['output']['message']['content']:
            if 'text' in content:
                answer += content['text']
        
        # Add the current exchange to the chat history
        chat_histories[session_id].append({"role": "user", "content": question, "timestamp": datetime.now().isoformat()})
        chat_histories[session_id].append({"role": "assistant", "content": answer, "timestamp": datetime.now().isoformat()})
        
        # Keep chat history to a reasonable size (last 10 exchanges)
        if len(chat_histories[session_id]) > 20:  # 10 user messages + 10 assistant responses
            chat_histories[session_id] = chat_histories[session_id][-20:]
        
        return answer, session_id
    
    except Exception as e:
        logger.error(f"Error asking Claude: {str(e)}")
        return f"Sorry, I couldn't process your question: {str(e)}", session_id

# Register the AI response function with Slack integration
try:
    slack_integration.set_ai_response_fn(lambda q: ask_claude(q)[0])
    logger.info("Registered AI response function with Slack integration")
except Exception as e:
    logger.warning(f"Failed to register AI function with Slack: {str(e)}")

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "healthy", "message": "API is running"})

@app.route('/ask', methods=['POST'])
def ask_question():
    """Endpoint to ask questions to the AI model."""
    try:
        data = request.json
        
        if not data or 'question' not in data:
            return jsonify({"error": "Missing question parameter"}), 400
        
        question = data['question']
        session_id = data.get('session_id')
        
        # Use the shared ask_claude function
        answer, session_id = ask_claude(question, session_id)
        
        # Return the response with session ID
        return jsonify({
            "answer": answer,
            "session_id": session_id,
            "model": CHAT_MODEL_ID,
            "usage": {
                "totalTokens": "N/A"  # We don't have access to token count in this simplified version
            }
        })
    
    except Exception as e:
        logger.error(f"Error in ask endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/chat_history', methods=['GET'])
def get_chat_history():
    """Endpoint to get chat history for a specific session."""
    try:
        session_id = request.args.get('session_id')
        
        if not session_id or session_id not in chat_histories:
            return jsonify({"error": "Invalid or missing session ID"}), 400
        
        return jsonify({
            "session_id": session_id,
            "history": chat_histories[session_id]
        })
    
    except Exception as e:
        logger.error(f"Error in chat_history endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    """Endpoint to clear chat history for a specific session."""
    try:
        data = request.json
        
        if not data or 'session_id' not in data:
            return jsonify({"error": "Missing session_id parameter"}), 400
        
        session_id = data['session_id']
        
        if session_id in chat_histories:
            chat_histories[session_id] = []
        
        return jsonify({
            "status": "success",
            "message": "Chat history cleared",
            "session_id": session_id
        })
    
    except Exception as e:
        logger.error(f"Error in clear_chat endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/search', methods=['POST'])
def search():
    """Endpoint to perform semantic search on the forum content."""
    try:
        data = request.json
        
        if not data or 'query' not in data:
            return jsonify({"error": "Missing query parameter"}), 400
        
        query = data['query']
        top_k = data.get('top_k', 5)  # Default to 5 results
        
        if vector_db is None:
            return jsonify({"error": "Vector database not initialized"}), 500
        
        # Perform semantic search
        results = []
        docs = vector_db.similarity_search(query, k=top_k)
        
        for doc in docs:
            results.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source", "Unknown"),
                "score": 0.0  # Scores not directly available from langchain_chroma
            })
        
        return jsonify({"results": results})
    
    except Exception as e:
        logger.error(f"Error in search endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/forums', methods=['GET'])
def get_forums():
    """Return list of available forums."""
    # Mock data - in a real app, this would come from a database
    forums = [
        {"id": 1, "name": "General Discussion", "description": "Talk about anything work-related"},
        {"id": 2, "name": "Technical Support", "description": "Get help with technical issues"},
        {"id": 3, "name": "Product Ideas", "description": "Share your ideas for new products or features"},
        {"id": 4, "name": "HR & Benefits", "description": "Discuss HR policies and benefits questions"}
    ]
    return jsonify({"forums": forums})

@app.route('/forum-threads/<int:forum_id>', methods=['GET'])
def get_forum_threads(forum_id):
    """Return threads for a specific forum."""
    # Map forum_id to forum name
    forum_map = {
        1: "General Discussion",
        2: "Technical Support",
        3: "Product Ideas",
        4: "HR & Benefits"
    }
    
    forum_name = forum_map.get(forum_id)
    if not forum_name:
        return jsonify({"error": "Forum not found"}), 404
    
    # Filter sample data by forum name to get relevant threads
    threads = []
    for item in data_loader.SAMPLE_DATA:
        if item["forum"] == forum_name:
            threads.append({
                "id": len(threads) + 1,
                "title": item["title"],
                "author": item["author"],
                "preview": item["content"].strip()[:100] + "...",
                "date": "2024-04-14"  # Mock date
            })
    
    return jsonify({"forum_id": forum_id, "forum_name": forum_name, "threads": threads})

def start_slack_in_thread():
    """Start the Slack bot in a separate thread."""
    try:
        slack_started = slack_integration.start_slack_bot()
        if slack_started:
            logger.info("Slack integration is running")
        else:
            logger.warning("Slack integration not started - you can still use the API endpoints")
    except Exception as e:
        logger.error(f"Error starting Slack integration: {str(e)}")
        logger.info("Continuing without Slack integration")

if __name__ == '__main__':
    # Start Slack integration in a separate thread
    try:
        slack_thread = threading.Thread(target=start_slack_in_thread)
        slack_thread.daemon = True  # This makes the thread exit when the main program exits
        slack_thread.start()
    except Exception as e:
        logger.error(f"Could not start Slack thread: {str(e)}")
        logger.info("REST API will still be available")
    
    # Start Flask app
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting Flask app on port {port}")
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False) 