#!/usr/bin/env python3
"""
X AI-Forum Integration Tests

This script tests the integration between the backend API and AI components.
"""

import requests
import json
import os
import logging
import sys
import time
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# API URL
API_URL = "http://localhost:8080"

def test_health():
    """Test the health endpoint."""
    try:
        response = requests.get(f"{API_URL}/health")
        data = response.json()
        
        logger.info(f"Health check response: {data}")
        
        assert response.status_code == 200
        assert data["status"] == "healthy"
        
        return True
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return False

def test_forums():
    """Test the forums endpoint."""
    try:
        response = requests.get(f"{API_URL}/forums")
        data = response.json()
        
        logger.info(f"Forums response: {data}")
        
        assert response.status_code == 200
        assert "forums" in data
        assert len(data["forums"]) > 0
        
        return True
    except Exception as e:
        logger.error(f"Forums check failed: {str(e)}")
        return False

def test_forum_threads():
    """Test the forum threads endpoint."""
    try:
        # Test a valid forum ID
        response = requests.get(f"{API_URL}/forum-threads/1")
        data = response.json()
        
        logger.info(f"Forum threads response: {data}")
        
        assert response.status_code == 200
        assert "threads" in data
        
        # Test an invalid forum ID
        response = requests.get(f"{API_URL}/forum-threads/999")
        assert response.status_code == 404
        
        return True
    except Exception as e:
        logger.error(f"Forum threads check failed: {str(e)}")
        return False

def test_ask():
    """Test the ask endpoint."""
    try:
        payload = {"question": "What is AWS Bedrock?"}
        
        response = requests.post(
            f"{API_URL}/ask",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        data = response.json()
        logger.info(f"Ask response: {data}")
        
        assert response.status_code == 200
        assert "answer" in data
        assert len(data["answer"]) > 0
        
        return True
    except Exception as e:
        logger.error(f"Ask check failed: {str(e)}")
        return False

def test_search():
    """Test the search endpoint."""
    try:
        payload = {"query": "AWS Bedrock setup"}
        
        response = requests.post(
            f"{API_URL}/search",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        data = response.json()
        logger.info(f"Search response: {data}")
        
        assert response.status_code == 200
        assert "results" in data
        
        return True
    except Exception as e:
        logger.error(f"Search check failed: {str(e)}")
        return False

def run_all_tests():
    """Run all integration tests."""
    logger.info("Starting integration tests...")
    
    tests = [
        ("Health check", test_health),
        ("Forums", test_forums),
        ("Forum threads", test_forum_threads),
        ("Ask endpoint", test_ask),
        ("Search endpoint", test_search)
    ]
    
    results = []
    
    for test_name, test_fn in tests:
        logger.info(f"Running test: {test_name}")
        try:
            result = test_fn()
            status = "PASSED" if result else "FAILED"
            results.append((test_name, status))
        except Exception as e:
            logger.error(f"Test {test_name} threw an exception: {str(e)}")
            results.append((test_name, "ERROR"))
    
    # Print summary
    logger.info("\n--- Test Results ---")
    for test_name, status in results:
        logger.info(f"{test_name}: {status}")
    
    # Count successful tests
    successful = len([r for r in results if r[1] == "PASSED"])
    logger.info(f"\nSuccessful tests: {successful}/{len(tests)}")

if __name__ == "__main__":
    run_all_tests() 