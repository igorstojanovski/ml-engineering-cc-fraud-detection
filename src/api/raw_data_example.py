"""
Example of how to use the API with raw transaction data
"""

import requests
import json

# API endpoint
API_URL = "http://localhost:5001"


def test_single_raw_prediction():
    """Test a single prediction with raw transaction data"""
    # Example raw transaction data
    transaction = {
        "trans_date_trans_time": "2020-06-21 12:14:25",
        "cc_num": "2291163933867244",
        "merchant": "fraud_Kirlin and Sons",
        "category": "personal_care",
        "amt": 2.86,
        "first": "Jeff",
        "last": "Elliott",
        "gender": "M",
        "street": "351 Darlene Green",
        "city": "Columbia",
        "state": "SC",
        "zip": "29209",
        "lat": 33.9659,
        "long": -80.9355,
        "city_pop": 333497,
        "job": "Mechanical engineer",
        "dob": "1968-03-19",
        "trans_num": "2da90c7d74bd46a0caf3777415b3ebd3",
        "unix_time": 1371816865,
        "merch_lat": 33.986391,
        "merch_long": -81.200714,
    }

    try:
        # Send request
        response = requests.post(
            f"{API_URL}/predict",
            json={"transaction_data": transaction},
            headers={"Content-Type": "application/json"},
        )

        print("Single Raw Prediction Response:")
        print(json.dumps(response.json(), indent=2))
        print(f"Status Code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API server for single prediction test.")
    except Exception as e:
        print(f"ERROR during single prediction test: {str(e)}")

    print("-" * 50)


def test_batch_raw_prediction():
    """Test batch predictions with raw transaction data"""
    # Example raw transactions
    transactions = [
        {
            "trans_date_trans_time": "2020-06-21 12:14:25",
            "cc_num": "2291163933867244",
            "merchant": "fraud_Kirlin and Sons",
            "category": "personal_care",
            "amt": 2.86,
            "first": "Jeff",
            "last": "Elliott",
            "gender": "M",
            "street": "351 Darlene Green",
            "city": "Columbia",
            "state": "SC",
            "zip": "29209",
            "lat": 33.9659,
            "long": -80.9355,
            "city_pop": 333497,
            "job": "Mechanical engineer",
            "dob": "1968-03-19",
            "trans_num": "2da90c7d74bd46a0caf3777415b3ebd3",
            "unix_time": 1371816865,
            "merch_lat": 33.986391,
            "merch_long": -81.200714,
        },
        {
            "trans_date_trans_time": "2020-06-21 12:14:33",
            "cc_num": "3573030041201292",
            "merchant": "fraud_Sporer-Keebler",
            "category": "personal_care",
            "amt": 29.84,
            "first": "Joanne",
            "last": "Williams",
            "gender": "F",
            "street": "3638 Marsh Union",
            "city": "Altonah",
            "state": "UT",
            "zip": "84002",
            "lat": 40.3207,
            "long": -110.436,
            "city_pop": 302,
            "job": "Sales professional, IT",
            "dob": "1990-01-17",
            "trans_num": "324cc204407e99f51b0d6ca0055005e7",
            "unix_time": 1371816873,
            "merch_lat": 39.450498,
            "merch_long": -109.960431,
        },
    ]

    try:
        # Send request
        response = requests.post(
            f"{API_URL}/predict",
            json={"transactions": transactions},
            headers={"Content-Type": "application/json"},
        )

        print("Batch Raw Prediction Response:")
        print(json.dumps(response.json(), indent=2))
        print(f"Status Code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API server for batch prediction test.")
    except Exception as e:
        print(f"ERROR during batch prediction test: {str(e)}")

    print("-" * 50)


if __name__ == "__main__":
    print("Testing Fraud Detection API with raw data...")

    # Test single prediction
    test_single_raw_prediction()

    # Test batch prediction
    test_batch_raw_prediction()
