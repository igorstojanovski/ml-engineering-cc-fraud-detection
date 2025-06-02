# Credit Card Fraud Detection ML Engineering Project

This project implements a machine learning system for credit card fraud detection with a complete MLOps pipeline including model training, evaluation, and deployment.

## Project Overview

The system uses machine learning models to detect potentially fraudulent credit card transactions. It includes:

- Multiple ML models (Decision Tree, Logistic Regression, XGBoost)
- Data preprocessing pipeline
- Model evaluation and comparison
- API for real-time and batch predictions
- Web frontend for interactive testing
- MLflow for experiment tracking
- DVC for data and model versioning

## Running locally

Do DVC pull first. This will bring in all the necessary dependencies for running the project locally.
Important files will be placed in the outputs folder.
The dependencies include decision_tree_model.pkl file and final_pipeline.pkl file. 
The decision_tree_model file has one example ML model which the backend can use for doing predictions.
The final_pipeline.pkl file ensures that the same preprocessing steps applied during model training are consistently applied to raw production data.
Credentials like username and password for the S3 bucket connected with DVC will be sent to you upon your request.
❗Without credentials DVC pill does not work.

## Running locally with Docker Compose

This project uses `docker-compose` to serve a locally running ML model with all necessary components.

### Prerequisites

1. Docker and Docker Compose installed
2. Copy `.env.example` to `.env` and fill in required values.
All values like keys and username / passwords will be provided to the project reviewers by email.
   ```bash
   cp .env.example .env
   ```

### Starting the services

To run the project:

```bash
docker compose up --build
```

Once running, you can access:
- Web frontend: http://localhost:3000
- API endpoint: http://localhost:5001
- MLflow UI: http://localhost:5000
- MinIO (S3-compatible storage): http://localhost:9001 (console)

## API Usage

### Batch Predictions

You can make batch predictions by sending a POST request to:

```
http://localhost:5001/predict
```

Example request body:

```json
{
  "transactions": [
    {
        "trans_date_trans_time": "2020-06-21 12:15:15",
        "cc_num": "3591919803438423",
        "merchant": "fraud_Haley Group",
        "category": "misc_pos",
        "amt": 6000000.05,
        "first": "Brian",
        "last": "",
        "gender": "",
        "street": "",
        "city": "",
        "state": "",
        "zip": "",
        "lat": 0,
        "long": 0,
        "city_pop": 0,
        "job": "Set designer",
        "dob": "1987-07-25",
        "trans_num": "2159175b9efe66dc301f149d3d5abf8c",
        "unix_time": 1371816915,
        "merch_lat": 28.812398,
        "merch_long": -80.883061
    },
    {
        "trans_date_trans_time": "2020-06-21 12:15:17",
        "cc_num": "3526826139003047",
        "merchant": "fraud_Johnston-Casper",
        "category": "travel",
        "amt": 3.19,
        "first": "Nathan",
        "last": "",
        "gender": "",
        "street": "",
        "city": "",
        "state": "",
        "zip": "",
        "lat": 0,
        "long": 0,
        "city_pop": 0,
        "job": "Furniture designer",
        "dob": "1955-07-06",
        "trans_num": "57ff021bd3f328f8738bb535c302a31b",
        "unix_time": 1371816917,
        "merch_lat": 44.959148,
        "merch_long": -85.884734
    }
  ]
}
```

## Development

For information about the development workflow using Git, DVC, and MLflow, see [Development Process](docs/development_process.md).

### Project Structure

- `src/`: Source code
  - `api/`: API implementation
  - `dataprocessing/`: Data preprocessing scripts
  - `frontend/`: Web UI implementation
  - `libs/`: Shared libraries
  - `models/`: ML model implementations
  - `proxy/`: Nginx configuration
  - `tests/`: Test suite
- `data/`: Training and test datasets (managed by DVC)
- `outputs/`: Model artifacts and preprocessed data
- `docs/`: Documentation

## CI/CD Pipeline

The project includes GitHub Actions workflows for continuous integration and deployment:
- Frontend CI: `frontend_ci.yml`
- ML Pipeline: `pipeline.yml`

For more details on the CI/CD flow, see `ci-cd-flow.md`.

## How to run the tests

under src/tests one can find various tests which are written in python
as such they are runnable as normal python file. 
Example:
```
/bin/python src/tests/test_distribution_drift.py
```

Some ML related tests use the training data specified under TRAIN_DATASET_FILE_NAME.
Other ML related tests use the model specified under the constant LOCAL_MODEL_PATH.
In order to have the data and the model run
```
DVC pull
```
for the very first time.
In order to run the tests for newly created data, specify the path to the data in TRAIN_DATASET_FILE_NAME
In order to run the tests for newly created model, specify the model under LOCAL_MODEL_PATH