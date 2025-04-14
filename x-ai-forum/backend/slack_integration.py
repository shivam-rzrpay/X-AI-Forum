import os
import logging
import time
import json
from flask import request, jsonify
import threading
import ssl
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create a custom SSL context with verification disabled
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Initialize the Slack app with the custom SSL context if tokens are available
app_token = os.getenv("SLACK_APP_TOKEN")
bot_token = os.getenv("SLACK_BOT_TOKEN")

slack_enabled = app_token and app_token.startswith("xapp-") and bot_token and not bot_token == "xoxb-YOUR_BOT_TOKEN"

if slack_enabled:
    try:
        # Initialize the Slack app with the custom SSL context
        slack_app = App(token=bot_token, ssl=ssl_context)
        logger.info("Slack app initialized with bot token")
    except Exception as e:
        logger.error(f"Failed to initialize Slack app: {str(e)}")
        slack_enabled = False
else:
    # Create a mock app for development
    class MockApp:
        def event(self, event_type):
            def decorator(func):
                return func
            return decorator
    
    slack_app = MockApp()
    logger.warning("Running with MOCK Slack integration - no real connection to Slack")

# Get the AI response function (will be passed from main app)
ai_response_fn = None

def set_ai_response_fn(fn):
    """Set the AI response function to use when responding to Slack messages."""
    global ai_response_fn
    ai_response_fn = fn
    logger.info("AI response function registered with Slack integration")

@slack_app.event("app_mention")
def handle_app_mentions(body, say):
    """Handle mentions of the bot in Slack."""
    try:
        # Extract the text and remove the bot mention
        text = body["event"]["text"]
        user = body["event"]["user"]
        # Remove the bot mention from the text (format: <@BOT_ID> text)
        question = text.split(">", 1)[1].strip() if ">" in text else text

        logger.info(f"Received question from Slack user {user}: {question}")

        # If we have an AI function, use it to get a response
        if ai_response_fn:
            # Send a typing indicator
            say("Thinking...")
            
            # Get response from AI
            response = ai_response_fn(question)
            
            # Reply in thread
            say(response)
        else:
            say("Sorry, I'm not connected to the AI service yet. Please try again later.")
    
    except Exception as e:
        logger.error(f"Error handling Slack mention: {str(e)}")
        say(f"Sorry, I encountered an error: {str(e)}")

def start_slack_bot():
    """Start the Slack bot in Socket Mode."""
    global slack_enabled
    
    if not slack_enabled:
        logger.warning("Slack integration disabled - missing valid tokens or configuration")
        return False
    
    try:
        # Start the socket mode handler
        handler = SocketModeHandler(slack_app, app_token)
        thread = threading.Thread(target=handler.start)
        thread.daemon = True
        thread.start()
        logger.info("Slack bot started in Socket Mode")
        return True
    except Exception as e:
        logger.error(f"Error starting Slack bot: {str(e)}")
        slack_enabled = False
        return False

if __name__ == "__main__":
    # For testing the Slack integration directly
    start_slack_bot() 