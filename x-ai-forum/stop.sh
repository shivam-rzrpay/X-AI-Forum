#!/bin/bash

# X AI-Forum Stop Script
# This script stops the backend and frontend services

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to log messages
log() {
    echo -e "$1"
    if [ -f "./x-ai-forum.log" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - $2" >> "./x-ai-forum.log"
    fi
}

# Function to stop the backend server
stop_backend() {
    if [ -f "backend.pid" ]; then
        PID=$(cat backend.pid)
        if ps -p "$PID" > /dev/null; then
            log "${YELLOW}Stopping backend server (PID: $PID)...${NC}" "Stopping backend server (PID: $PID)..."
            kill "$PID"
            # Wait for process to terminate
            for i in {1..5}; do
                if ! ps -p "$PID" > /dev/null; then
                    break
                fi
                sleep 1
            done
            
            # Check if process still exists
            if ps -p "$PID" > /dev/null; then
                log "${YELLOW}Backend server still running. Force killing...${NC}" "Backend server still running. Force killing..."
                kill -9 "$PID" 2>/dev/null
            fi
            
            log "${GREEN}Backend server stopped.${NC}" "Backend server stopped."
        else
            log "${YELLOW}Backend server not running (PID: $PID).${NC}" "Backend server not running (PID: $PID)."
        fi
        rm -f backend.pid
    else
        log "${YELLOW}Backend PID file not found.${NC}" "Backend PID file not found."
        # Try to find and kill any Flask processes
        PIDS=$(ps aux | grep "python.*app.py" | grep -v grep | awk '{print $2}')
        if [ -n "$PIDS" ]; then
            log "${YELLOW}Found Flask processes: $PIDS. Stopping...${NC}" "Found Flask processes: $PIDS. Stopping..."
            for PID in $PIDS; do
                kill "$PID" 2>/dev/null
            done
            log "${GREEN}Stopped Flask processes.${NC}" "Stopped Flask processes."
        else
            log "${YELLOW}No Flask processes found.${NC}" "No Flask processes found."
        fi
    fi
}

# Function to stop the frontend server
stop_frontend() {
    if [ -f "frontend.pid" ]; then
        PID=$(cat frontend.pid)
        if ps -p "$PID" > /dev/null; then
            log "${YELLOW}Stopping frontend server (PID: $PID)...${NC}" "Stopping frontend server (PID: $PID)..."
            kill "$PID"
            # Wait for process to terminate
            for i in {1..3}; do
                if ! ps -p "$PID" > /dev/null; then
                    break
                fi
                sleep 1
            done
            
            # Check if process still exists
            if ps -p "$PID" > /dev/null; then
                log "${YELLOW}Frontend server still running. Force killing...${NC}" "Frontend server still running. Force killing..."
                kill -9 "$PID" 2>/dev/null
            fi
            
            log "${GREEN}Frontend server stopped.${NC}" "Frontend server stopped."
        else
            log "${YELLOW}Frontend server not running (PID: $PID).${NC}" "Frontend server not running (PID: $PID)."
        fi
        rm -f frontend.pid
    else
        log "${YELLOW}Frontend PID file not found.${NC}" "Frontend PID file not found."
        # Try to find and kill any http-server processes
        PIDS=$(ps aux | grep "http[-.]server" | grep -v grep | awk '{print $2}')
        if [ -n "$PIDS" ]; then
            log "${YELLOW}Found http-server processes: $PIDS. Stopping...${NC}" "Found http-server processes: $PIDS. Stopping..."
            for PID in $PIDS; do
                kill "$PID" 2>/dev/null
            done
            log "${GREEN}Stopped http-server processes.${NC}" "Stopped http-server processes."
        else
            PIDS=$(ps aux | grep "python.*http.server" | grep -v grep | awk '{print $2}')
            if [ -n "$PIDS" ]; then
                log "${YELLOW}Found Python HTTP server processes: $PIDS. Stopping...${NC}" "Found Python HTTP server processes: $PIDS. Stopping..."
                for PID in $PIDS; do
                    kill "$PID" 2>/dev/null
                done
                log "${GREEN}Stopped Python HTTP server processes.${NC}" "Stopped Python HTTP server processes."
            else
                log "${YELLOW}No frontend server processes found.${NC}" "No frontend server processes found."
            fi
        fi
    fi
}

# Stop servers
log "${YELLOW}Stopping X AI-Forum servers...${NC}" "Stopping X AI-Forum servers..."
stop_backend
stop_frontend

# Clean up temporary files (optional)
# log "${YELLOW}Cleaning up temporary files...${NC}" "Cleaning up temporary files..."
# rm -f backend.log frontend.log

# Final message
log "${GREEN}X AI-Forum servers stopped.${NC}" "X AI-Forum servers stopped."
log "${GREEN}To start the servers again, run: ./start.sh${NC}" "To start the servers again, run: ./start.sh" 