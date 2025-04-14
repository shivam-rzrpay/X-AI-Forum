#!/usr/bin/env python3
"""
X AI-Forum Slack Setup Helper

This script helps configure the Slack integration for X AI-Forum by:
1. Checking for required environment variables
2. Testing connections to Slack
3. Updating the .env file if needed
"""

import os
import re
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_env_var(var_name, pattern=None, required=True):
    """Check if an environment variable exists and matches a pattern."""
    value = os.getenv(var_name)
    
    if not value:
        if required:
            logger.error(f"Missing environment variable: {var_name}")
            return False
        else:
            logger.warning(f"Optional environment variable not set: {var_name}")
            return None
    
    if pattern and not re.match(pattern, value):
        logger.error(f"Invalid format for {var_name}. Expected pattern: {pattern}")
        return False
    
    return value

def prompt_for_value(var_name, pattern=None, default=None, secret=False):
    """Prompt the user for an environment variable value."""
    prompt_text = f"Enter your {var_name}"
    if default:
        prompt_text += f" (default: {default})"
    prompt_text += ": "
    
    while True:
        if secret:
            # Use getpass if available, otherwise fallback to input
            try:
                import getpass
                value = getpass.getpass(prompt_text)
            except ImportError:
                value = input(prompt_text)
        else:
            value = input(prompt_text)
        
        # Use default if empty
        if not value and default:
            value = default
            
        # Verify pattern if provided
        if pattern and not re.match(pattern, value):
            logger.error(f"Invalid format. Expected pattern: {pattern}")
            continue
            
        return value

def update_env_file(env_vars):
    """Update the .env file with new values."""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    
    # Read existing .env file
    try:
        with open(env_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []
    
    # Process or add each variable
    for var_name, value in env_vars.items():
        var_pattern = re.compile(f"^{var_name}=.*$")
        var_line = f"{var_name}={value}\n"
        
        # Find and replace existing line, or append if not found
        for i, line in enumerate(lines):
            if var_pattern.match(line):
                lines[i] = var_line
                break
        else:
            lines.append(var_line)
    
    # Write back to .env file
    with open(env_path, 'w') as f:
        f.writelines(lines)
    
    logger.info(f"Updated .env file at {env_path}")

def verify_slack_tokens():
    """Verify the Slack tokens."""
    # Load environment variables
    load_dotenv()
    
    # Check Slack tokens
    app_token = check_env_var("SLACK_APP_TOKEN", r"^xapp-\d-[A-Z0-9]+-\d+-[a-f0-9]+$", required=False)
    bot_token = check_env_var("SLACK_BOT_TOKEN", r"^xoxb-\d+-\d+-[a-zA-Z0-9]+$", required=False)
    
    # If tokens not found or invalid, prompt for them
    env_updates = {}
    
    if not app_token:
        logger.warning("SLACK_APP_TOKEN not found or invalid")
        logger.info("You can find your app token at https://api.slack.com/apps > Your App > Socket Mode")
        app_token = prompt_for_value("SLACK_APP_TOKEN", r"^xapp-\d-[A-Z0-9]+-\d+-[a-f0-9]+$")
        env_updates["SLACK_APP_TOKEN"] = app_token
    else:
        logger.info("SLACK_APP_TOKEN is valid")
    
    if not bot_token:
        logger.warning("SLACK_BOT_TOKEN not found or invalid")
        logger.info("You can find your bot token at https://api.slack.com/apps > Your App > OAuth & Permissions > Bot User OAuth Token")
        bot_token = prompt_for_value("SLACK_BOT_TOKEN", r"^xoxb-\d+-\d+-[a-zA-Z0-9]+$")
        env_updates["SLACK_BOT_TOKEN"] = bot_token
    else:
        logger.info("SLACK_BOT_TOKEN is valid")
    
    # Ask for signing secret (optional)
    signing_secret = check_env_var("SLACK_SIGNING_SECRET", required=False)
    if not signing_secret:
        logger.info("SLACK_SIGNING_SECRET is optional but recommended for enhanced security")
        logger.info("You can find it at https://api.slack.com/apps > Your App > Basic Information > App Credentials > Signing Secret")
        if input("Would you like to add it now? (y/n): ").lower() == 'y':
            signing_secret = prompt_for_value("SLACK_SIGNING_SECRET", secret=True)
            env_updates["SLACK_SIGNING_SECRET"] = signing_secret
    else:
        logger.info("SLACK_SIGNING_SECRET is set")
    
    # Update .env file if needed
    if env_updates:
        update_env_file(env_updates)
    
    # Final check
    if app_token and bot_token:
        logger.info("Slack tokens are configured and ready to use")
        return True
    else:
        logger.error("Slack configuration incomplete")
        return False

def test_slack_connection():
    """Test the connection to Slack."""
    try:
        from slack_sdk import WebClient
        from slack_sdk.errors import SlackApiError
        
        client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
        response = client.auth_test()
        
        if response["ok"]:
            logger.info(f"Successfully connected to Slack as {response['user']} in workspace {response['team']}")
            return True
        else:
            logger.error("Slack connection test failed")
            return False
            
    except SlackApiError as e:
        logger.error(f"Slack API error: {e.response['error']}")
        return False
    except Exception as e:
        logger.error(f"Error testing Slack connection: {str(e)}")
        return False

def main():
    """Main function to run the setup process."""
    logger.info("=== X AI-Forum Slack Setup Helper ===")
    
    # Verify tokens
    if not verify_slack_tokens():
        logger.error("Please configure your Slack tokens and try again")
        sys.exit(1)
    
    # Test connection
    logger.info("Testing connection to Slack...")
    if test_slack_connection():
        logger.info("✅ Slack integration is properly configured!")
        logger.info("You can now start the application with: python app.py")
    else:
        logger.error("❌ Slack connection test failed")
        logger.error("Please check your tokens and permissions, then try again")
        sys.exit(1)

if __name__ == "__main__":
    main() 