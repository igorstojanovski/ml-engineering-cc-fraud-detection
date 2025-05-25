"""
Example client script to demonstrate how to use the fraud detection API
"""

import json
import os
import subprocess
import sys
import time

import requests

# API endpoint
API_URL = "http://127.0.0.1:5001"

# Flag to track if we started the server
server_process = None


def start_api_server():
    """Start the API server if it's not already running"""
    global server_process
    try:
        # Check if server is already running
        print("API server is already running.")
        return True
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print("API server is not running. Starting it now...")

        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Start the server as a subprocess
        server_process = subprocess.Popen(
            [sys.executable, os.path.join(current_dir, "api.py")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait for server to start (up to 10 seconds)
        for _ in range(10):
            try:
                print("API server started successfully.")
                return True
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                time.sleep(1)

        print("Failed to start API server.")
        return False


def stop_api_server():
    """Stop the API server if we started it"""
    if server_process:
        print("Stopping API server...")
        server_process.terminate()
        server_process.wait(timeout=5)
        print("API server stopped.")


def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{API_URL}/health")
        print("Health Check Response:")
        print(json.dumps(response.json(), indent=2))
        print(f"Status Code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API server. Make sure it's running.")
    print("-" * 50)


def test_single_prediction():
    """Test a single prediction with real data from the validation_preprocessed.csv"""
    # Example transaction data from validation_preprocessed.csv
    transaction = {
        "category": 0.7692307692307693,
        "gender": 1,
        "transaction_hour": 0.5217391304347826,
        "transaction_month": 0.0,
        "is_weekend": 1,
        "day_of_week": 0.5,
        "part_of_day": 0.0,
        "age": 0.4567901234567901,
        "distance": 0.16205439081001802,
        "city_pop_bin": 0.0,
        "amt_yeo_johnson": 0.043759851582931636,
    }

    try:
        # Send request
        response = requests.post(
            f"{API_URL}/predict",
            json={"transaction_data": transaction},
            headers={"Content-Type": "application/json"},
        )

        print("Single Prediction Response:")
        print(json.dumps(response.json(), indent=2))
        print(f"Status Code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API server for single prediction test.")
    except Exception as e:
        print(f"ERROR during single prediction test: {str(e)}")

    print("-" * 50)


def test_batch_prediction():
    """Test batch predictions with real data from validation_preprocessed.csv"""
    # Example transactions from validation_preprocessed.csv
    transactions = [
        {
            "category": 0.7692307692307693,
            "gender": 1,
            "transaction_hour": 0.5217391304347826,
            "transaction_month": 0.0,
            "is_weekend": 1,
            "day_of_week": 0.5,
            "part_of_day": 0.0,
            "age": 0.4567901234567901,
            "distance": 0.16205439081001802,
            "city_pop_bin": 0.0,
            "amt_yeo_johnson": 0.043759851582931636,
        },
        {
            "category": 0.7692307692307693,
            "gender": 0,
            "transaction_hour": 0.5217391304347826,
            "transaction_month": 0.0,
            "is_weekend": 1,
            "day_of_week": 0.5,
            "part_of_day": 0.0,
            "age": 0.18518518518518517,
            "distance": 0.6949745858768592,
            "city_pop_bin": 0.8,
            "amt_yeo_johnson": 0.20283470583231186,
        },
        {
            "category": 0.38461538461538464,
            "gender": 0,
            "transaction_hour": 0.5217391304347826,
            "transaction_month": 0.0,
            "is_weekend": 1,
            "day_of_week": 0.5,
            "part_of_day": 0.0,
            "age": 0.43209876543209874,
            "distance": 0.39095977319524644,
            "city_pop_bin": 0.2,
            "amt_yeo_johnson": 0.23004177642877963,
        },
    ]

    try:
        # Send request
        response = requests.post(
            f"{API_URL}/predict",
            json={"transactions": transactions},
            headers={"Content-Type": "application/json"},
        )

        print("Batch Prediction Response:")
        print(json.dumps(response.json(), indent=2))
        print(f"Status Code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API server for batch prediction test.")
    except Exception as e:
        print(f"ERROR during batch prediction test: {str(e)}")

    print("-" * 50)


if __name__ == "__main__":
    print("Testing Fraud Detection API...")

    try:
        # Start the API server if it's not running
        if start_api_server():
            # Give the server a moment to fully initialize
            time.sleep(2)

            # Test health endpoint
            test_health()

            # Test single prediction
            test_single_prediction()

            # Test batch prediction
            test_batch_prediction()
    except Exception as e:
        print(f"Error during API testing: {str(e)}")
    finally:
        # Stop the API server if we started it
        stop_api_server()
