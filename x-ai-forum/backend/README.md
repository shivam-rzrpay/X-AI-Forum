# X AI-Forum Backend

This is the backend for the X AI-Forum application, an internal discussion forum powered by AWS Bedrock with Slack integration.

## Features

- REST API built with Flask
- AI-powered question answering using Claude 3 Sonnet
- Semantic search using Amazon Titan Embeddings
- Vector database storage with ChromaDB
- Slack integration using Socket Mode

## Setup

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure AWS credentials:
   - Ensure you have the AWS CLI configured with a profile that has access to AWS Bedrock
   - Edit the `.env` file with your AWS profile and region

4. Configure Slack integration:
   - Create a Slack app at api.slack.com/apps
   - Configure bot scopes: app_mentions:read, chat:write, channels:history, channels:read, groups:history, groups:read, im:history, im:read
   - Install the app to your workspace and get the Bot User OAuth Token
   - Enable Socket Mode and get an App-Level Token
   - Add the tokens to your `.env` file (see below)

5. Initialize the vector database:
   ```
   python data_loader.py
   ```

6. Start the server:
   ```
   python app.py
   ```

7. Run integration tests:
   ```
   python test_integration.py
   ```

## API Endpoints

- `GET /health` - Health check
- `GET /forums` - List all forums
- `GET /forum-threads/<forum_id>` - Get threads for a specific forum
- `POST /ask` - Ask a question to the AI assistant
  - Request body: `{"question": "Your question here"}`
- `POST /search` - Perform semantic search on forum content
  - Request body: `{"query": "Your search query", "top_k": 5}`

## Environment Variables

Create a `.env` file with the following variables:

```
# AWS Configuration
AWS_REGION=ap-south-1
AWS_PROFILE=your-aws-profile
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
PORT=8080

# Slack Integration (optional)
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
```

## File Structure

- `app.py`