import json  # Add this import for JSON handling
import logging
import boto3
from botocore.exceptions import ClientError
import psycopg2
from datetime import datetime
import time
import os
from toolsConfigCs import tools

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# First try to use the model directly
model_id = os.getenv('FRIDAY_SONNET_V2_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')

def check_sr_with_timeframe(merchant_id, start_time_frame, end_time_frame, method):
    """
    Mock function to return settlement rate information.
    In a real application, this would query a database.
    """
    # Mock data for demonstration
    if method.upper() == "UPI":
        return {
            "merchant_id": merchant_id,
            "time_period": f"{start_time_frame} to {end_time_frame}",
            "method": method,
            "settlement_rates": [
                {"date": "2023-03-01", "rate": "0.85%"},
                {"date": "2023-03-15", "rate": "0.82%"},
                {"date": "2023-04-01", "rate": "0.80%"},
                {"date": "2023-04-15", "rate": "0.79%"},
                {"date": "2023-04-30", "rate": "0.78%"}
            ],
            "average_rate": "0.81%"
        }
    else:
        return {
            "merchant_id": merchant_id,
            "time_period": f"{start_time_frame} to {end_time_frame}",
            "method": method,
            "error": "Data not available for this payment method"
        }

def handle_tool_usage(response):
    """Handle tool usage from the model response"""
    if response['stopReason'] == 'tool_use':
        print("\nModel wants to use tools:")
        tools_called = []
        
        for content in response['output']['message']['content']:
            if 'toolUse' in content:
                tool = content['toolUse']
                tool_name = tool['name']
                tool_inputs = tool['input']
                print(f"Tool: {tool_name}")
                print(f"Inputs: {json.dumps(tool_inputs, indent=2)}")
                
                if tool_name == 'check_sr_with_timeframe':
                    merchant_id = tool_inputs.get('merchant_id', '')
                    start_time_frame = tool_inputs.get('start_time_frame', '')
                    end_time_frame = tool_inputs.get('end_time_frame', '')
                    method = tool_inputs.get('method', '')
                    
                    print(f"Merchant ID: {merchant_id}")
                    print(f"Start Time Frame: {start_time_frame}")
                    print(f"End Time Frame: {end_time_frame}")
                    print(f"Method: {method}")
                    
                    result = check_sr_with_timeframe(merchant_id, start_time_frame, end_time_frame, method)
                    print(f"Tool Result: {json.dumps(result, indent=2)}")
                    tools_called.append({
                        "name": tool_name,
                        "result": result
                    })
        
        return tools_called
    
    return None

# Main function
if __name__ == "__main__":
    try:
        # Create a Bedrock runtime client with explicit region and profile
        print("Creating AWS Bedrock session...")
        session = boto3.Session(profile_name='AWS_101860328116_bedrock-101860328116')
        bedrock_client = session.client('bedrock-runtime', region_name='ap-south-1')
        
        # Available models to try
        models = [
            model_id,  # Try the configured model first 
            "anthropic.claude-3-sonnet-20240229-v1:0",
            "anthropic.claude-3-haiku-20240307-v1:0"
        ]
        
        # System prompts to use
        system_prompt = [{"text": "You are a customer support assistant for RazorPay, a payment processing company. You can help with transaction settlement rates. Use the check_sr_with_timeframe tool when asked about settlement rates."}]
        
        # User message
        user_message = [
            {
                "role": "user",
                "content": [{"text": "Can you send the SR of zomato for the last 2 months for UPI?"}]
            }
        ]
        
        # Try each model
        for current_model in models:
            try:
                print(f"\nTrying model: {current_model}")
                
                # Call the model with tool configuration
                response = bedrock_client.converse(
                    modelId=current_model,
                    messages=user_message,
                    system=system_prompt,
                    inferenceConfig={"temperature": 0.7, "topP": 0.9},
                    toolConfig=tools()
                )
                
                print("\nModel Response:")
                for content in response['output']['message']['content']:
                    if 'text' in content:
                        print(content['text'])
                
                # Handle tool usage if any
                tools_called = handle_tool_usage(response)
                if tools_called:
                    print("\nTool was called successfully!")
                    for tool in tools_called:
                        print(f"Tool: {tool['name']}")
                        print(f"Result: {json.dumps(tool['result'], indent=2)}")
                
                print(f"\nModel Stats:")
                print(f"Model ID: {current_model}")
                print(f"Stop Reason: {response['stopReason']}")
                print(f"Usage: {response['usage']}")
                
                # If we got here, we found a working model
                break
                
            except ClientError as e:
                logger.error(f"Error with model {current_model}: {str(e)}")
                continue
    
    except Exception as e:
        logger.error(f"Failed to generate conversation: {str(e)}")