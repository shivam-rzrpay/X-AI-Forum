# X AI-Forum

A modern internal discussion forum powered by AWS Bedrock, featuring AI capabilities with Claude and semantic search with Titan Embeddings. Now with Slack integration!

## Project Overview

X AI-Forum is an internal company forum that demonstrates the capabilities of generative AI in enhancing workplace communication and knowledge management. The application features:

- Standard forum functionality for discussions and threads
- AI assistant powered by Claude 3 Sonnet via AWS Bedrock
- Semantic search capabilities using Amazon Titan Embeddings
- Vector database storage with ChromaDB
- Slack integration for using the AI assistant directly from Slack

## Architecture

The project follows a client-server architecture:

- **Frontend**: HTML, CSS, and JavaScript with Bootstrap for UI components
- **Backend**: Python Flask API with AWS Bedrock integration
- **Database**: ChromaDB for vector storage (development/demo only)
- **Slack Integration**: Socket Mode connection for Slack bot functionality

## Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js (for serving the frontend, optional)
- AWS account with Bedrock access
- AWS CLI configured
- Slack workspace with admin permissions

### Slack App Setup

1. Go to [api.slack.com/apps](https://api.slack.com/apps) and log in
2. Create a new app by clicking "Create New App" > "From scratch"
3. Enter app name (e.g., "X AI-Forum") and select your workspace
4. Configure bot scopes:
   - Go to "OAuth & Permissions"
   - Add scopes: `app_mentions:read`, `chat:write`, `channels:history`, `channels:read`, `groups:history`, `groups:read`, `im:history`, `im:read`
5. Install the app to your workspace
6. Copy the Bot User OAuth Token (starts with `xoxb-...`)
7. Enable Socket Mode:
   - Go to "Socket Mode" in the sidebar
   - Toggle "Enable Socket Mode"
   - Generate an app-level token (starts with `xapp-...`)
8. Configure Event Subscriptions:
   - Go to "Event Subscriptions"
   - Toggle "Enable Events" to ON
   - Subscribe to bot events: `app_mention`
   - Save changes

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure your environment variables in `.env`:
   ```
   # AWS Configuration
   AWS_REGION=ap-south-1
   AWS_PROFILE=your-aws-profile
   BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
   PORT=8080
   
   # Slack Integration
   SLACK_APP_TOKEN=xapp-your-app-token
   SLACK_BOT_TOKEN=xoxb-your-bot-token
   SLACK_SIGNING_SECRET=your-signing-secret
   ```

5. Initialize the vector database:
   ```
   python data_loader.py
   ```

6. Start the backend server:
   ```
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. You can serve the frontend using any static file server. For example, with Python:
   ```
   python -m http.server 8080
   ```

3. Or with Node.js's http-server:
   ```
   npx http-server -p 8080
   ```

4. Open your browser and visit `http://localhost:8080`

## Using the Slack Integration

Once your server is running and your Slack app is configured:

1. Invite the bot to a channel using `/invite @X-AI-Forum`
2. Ask questions by mentioning the bot: `@X-AI-Forum What is AWS Bedrock?`
3. The bot will respond with answers using Claude AI

## API Documentation

The backend provides the following REST API endpoints:

- `GET /health` - Health check
- `GET /forums` - List all forums
- `GET /forum-threads/<forum_id>` - Get threads for a specific forum
- `POST /ask` - Ask a question to the AI assistant
  - Request body: `{"question": "Your question here"}`
- `POST /search` - Perform semantic search on forum content
  - Request body: `{"query": "Your search query", "top_k": 5}`

## AWS Bedrock Configuration

The application uses the following AWS Bedrock models:
- Anthropic Claude 3 Sonnet for the AI assistant
- Amazon Titan Embeddings for semantic search

Ensure you have requested access to these models in your AWS account.

## Testing

To test the integration between the frontend, backend, and Slack:

```
cd backend
python test_integration.py
```

This will run tests against all the key endpoints and verify that everything is functioning correctly.

## Future Enhancements

Potential areas for expansion:
- User authentication and authorization
- Persistent database for forums, threads, and users
- Real-time notifications
- Mobile responsiveness improvements
- Admin dashboard
- File attachments
- Rich text formatting 