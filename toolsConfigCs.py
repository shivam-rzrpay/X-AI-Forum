def tools():
    """
    Returns the tools configuration for AWS Bedrock API.
    """
    return {
        "tools": [
            {
                "toolSpec": {
                    "name": "check_sr_with_timeframe",
                    "description": "Get settlement rate information for a merchant within a specific time frame",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "merchant_id": {
                                    "type": "string",
                                    "description": "The ID of the merchant"
                                },
                                "start_time_frame": {
                                    "type": "string",
                                    "description": "The start date of the time frame (YYYY-MM-DD)"
                                },
                                "end_time_frame": {
                                    "type": "string",
                                    "description": "The end date of the time frame (YYYY-MM-DD)"
                                },
                                "method": {
                                    "type": "string",
                                    "description": "The payment method (e.g., UPI, Credit Card)"
                                }
                            },
                            "required": ["merchant_id", "start_time_frame", "end_time_frame", "method"]
                        }
                    }
                }
            }
        ]
    } 