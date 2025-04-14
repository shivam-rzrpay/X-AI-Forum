# AWS Bedrock Integration

This project demonstrates integration with AWS Bedrock using Claude models to process customer queries.

## Setup

### 1. Install Dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 2. AWS Configuration

#### Option 1: AWS SSO Login (Recommended)

```bash
aws configure sso
```

Enter the following details when prompted:
- SSO session name: xassist
- SSO start URL: https://d-9f6706151a.awsapps.com/start/#
- SSO region: ap-south-1
- SSO registration scopes: sso:account:access

Follow the browser authentication process, and select:
- Account: 101860328116
- Role: AWS_101860328116_bedrock

#### Option 2: Standard AWS Credentials

```bash
aws configure
```

Set your AWS Access Key, Secret Key, and default region.

### 3. AWS Bedrock Inference Profile (Optional)

The script will try to use different Claude models available in your region. However, for production use, you should:

1. Go to AWS Bedrock console in your region
2. Navigate to "Inference profiles" under "Model access"
3. Create a new inference profile selecting one of the following models:
   - Claude 3.5 Sonnet v2
   - Claude 3 Sonnet
   - Claude 3 Haiku
4. Set the provisioned throughput settings as needed
5. Copy the inference profile ID and set it as the environment variable below

### 4. Environment Variables

Set the following environment variables (optional, defaults are provided in the code):

```bash
# Only set this if you created an inference profile
export FRIDAY_SONNET_V2_MODEL_ID=your-inference-profile-id
```

## Running the Application

```bash
python3 bedrock.py
```

## Tool Usage

The script successfully calls the check_sr_with_timeframe tool and receives mock data. However, the complete tool usage cycle (returning tool results back to the model) may require additional configuration in an inference profile.

To fully implement tool usage with result handling:

1. Create a dedicated inference profile in AWS Bedrock
2. Set the correct permissions for the model to use tools
3. Update the API call formats based on the most recent AWS Bedrock documentation

## Troubleshooting

If you encounter authentication issues, verify that:
1. Your AWS credentials have permissions for Amazon Bedrock
2. The models are available in your AWS region
3. The region in the code matches your AWS configuration
4. For SSO, ensure your session is active by running `aws sso login --profile AWS_101860328116_bedrock-101860328116`
5. If you need to use the script for production, create an inference profile as described above 