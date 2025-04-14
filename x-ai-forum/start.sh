#!/bin/bash

# X AI-Forum Start Script
# This script starts both the backend and frontend services

# Configuration
BACKEND_DIR="./backend"
FRONTEND_DIR="./frontend"
BACKEND_PORT=8080
FRONTEND_PORT=8080
LOGFILE="./x-ai-forum.log"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to log messages
log() {
    echo -e "$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $2" >> "$LOGFILE"
}

# Check for required tools
if ! command_exists python3; then
    log "${RED}Error: python3 is not installed.${NC}" "ERROR: python3 is not installed."
    exit 1
fi

# Initialize log file
echo "=== X AI-Forum Log $(date '+%Y-%m-%d %H:%M:%S') ===" > "$LOGFILE"

# Function to start the backend
start_backend() {
    log "${YELLOW}Starting backend server...${NC}" "Starting backend server..."
    
    # Change to backend directory
    cd "$BACKEND_DIR" || { 
        log "${RED}Error: Backend directory not found.${NC}" "ERROR: Backend directory not found."
        exit 1
    }
    
    # Check for virtual environment
    if [ ! -d "venv" ]; then
        log "${YELLOW}Virtual environment not found. Creating...${NC}" "Virtual environment not found. Creating..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate || {
        log "${RED}Error: Failed to activate virtual environment.${NC}" "ERROR: Failed to activate virtual environment."
        exit 1
    }
    
    # Check for required packages
    if [ ! -f "requirements.txt" ]; then
        log "${RED}Error: requirements.txt not found.${NC}" "ERROR: requirements.txt not found."
        exit 1
    fi
    
    # Install dependencies
    log "${YELLOW}Installing dependencies...${NC}" "Installing dependencies..."
    pip install -r requirements.txt
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        log "${YELLOW}Warning: .env file not found. Creating from example...${NC}" "Warning: .env file not found."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log "${YELLOW}Created .env from .env.example. Please update with your credentials.${NC}" "Created .env from .env.example."
        else
            # Create minimal .env file
            cat > .env << EOF
AWS_REGION=ap-south-1
AWS_PROFILE=default
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
PORT=$BACKEND_PORT

# Slack Integration
# SLACK_APP_TOKEN=xapp-1-...
# SLACK_BOT_TOKEN=xoxb-...
# SLACK_SIGNING_SECRET=...
EOF
            log "${YELLOW}Created minimal .env file. Please update with your credentials.${NC}" "Created minimal .env file."
        fi
    fi
    
    # Setup Slack (optional)
    if grep -q "SLACK_APP_TOKEN=xapp-1-" .env && grep -q "SLACK_BOT_TOKEN=xoxb-" .env; then
        log "${GREEN}Slack seems to be configured.${NC}" "Slack seems to be configured."
    else
        log "${YELLOW}Slack not configured. Run 'python setup_slack.py' to configure it.${NC}" "Slack not configured."
    fi
    
    # Initialize Vector DB if it doesn't exist
    if [ ! -d "vector_db" ]; then
        log "${YELLOW}Vector database not found. Initializing...${NC}" "Vector database not found. Initializing..."
        python data_loader.py
    fi
    
    # Start the Flask server in the background
    log "${GREEN}Starting Flask server on port $BACKEND_PORT...${NC}" "Starting Flask server on port $BACKEND_PORT..."
    python app.py > ../backend.log 2>&1 &
    BACKEND_PID=$!
    
    # Save the PID
    echo "$BACKEND_PID" > ../backend.pid
    
    log "${GREEN}Backend server started with PID $BACKEND_PID${NC}" "Backend server started with PID $BACKEND_PID"
    
    # Return to the root directory
    cd ..
}

# Function to start the frontend
start_frontend() {
    log "${YELLOW}Starting frontend server...${NC}" "Starting frontend server..."
    
    # Change to frontend directory
    cd "$FRONTEND_DIR" || { 
        log "${RED}Error: Frontend directory not found.${NC}" "ERROR: Frontend directory not found."
        exit 1
    }
    
    # Determine the best way to serve frontend
    if command_exists npx; then
        log "${GREEN}Using npx to serve frontend...${NC}" "Using npx to serve frontend..."
        npx http-server -p "$FRONTEND_PORT" > ../frontend.log 2>&1 &
        FRONTEND_PID=$!
    elif command_exists python3; then
        log "${GREEN}Using Python to serve frontend...${NC}" "Using Python to serve frontend..."
        python3 -m http.server "$FRONTEND_PORT" > ../frontend.log 2>&1 &
        FRONTEND_PID=$!
    else
        log "${RED}Error: No suitable method found to serve frontend.${NC}" "ERROR: No suitable method found to serve frontend."
        exit 1
    fi
    
    # Save the PID
    echo "$FRONTEND_PID" > ../frontend.pid
    
    log "${GREEN}Frontend server started with PID $FRONTEND_PID${NC}" "Frontend server started with PID $FRONTEND_PID"
    
    # Return to the root directory
    cd ..
}

# Start services
start_backend
start_frontend

# Display access information
echo ""
log "${GREEN}====================================${NC}" "Services started successfully."
log "${GREEN}X AI-Forum started successfully!${NC}" "X AI-Forum started successfully."
log "${GREEN}====================================${NC}" ""
log "${GREEN}Backend API: http://localhost:$BACKEND_PORT${NC}" "Backend API: http://localhost:$BACKEND_PORT"
log "${GREEN}Frontend UI: http://localhost:$FRONTEND_PORT${NC}" "Frontend UI: http://localhost:$FRONTEND_PORT"
log "${GREEN}====================================${NC}" ""
log "${YELLOW}Log files:${NC}" "Log files:"
log "${YELLOW}- Backend: ./backend.log${NC}" "- Backend: ./backend.log"
log "${YELLOW}- Frontend: ./frontend.log${NC}" "- Frontend: ./frontend.log"
log "${YELLOW}- Combined: $LOGFILE${NC}" "- Combined: $LOGFILE"
echo ""
log "${GREEN}To stop the servers, run: ./stop.sh${NC}" "To stop the servers, run: ./stop.sh"
echo "" 