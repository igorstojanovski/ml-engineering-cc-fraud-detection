# fraud-detection-ml-engineering
A repository for the PA2595 Machine Learning Engineering BTH Course

## API Usage

The project includes a REST API for making fraud predictions using the trained model.

### Starting the API Server

```bash
python -m src.api.run_api
```

The API will be available at http://localhost:5001

### API Endpoints

#### Health Check
```
GET /health
```
Returns the health status of the API and whether the model is loaded.

#### Make Prediction
```
POST /predict
```

Example request body for a single transaction:
```json
{
  "transaction_data": {
    "cc_num": "2703186189652095",
    "merchant": "fraud_Rippin, Kub and Mann",
    "category": "misc_net",
    "amt": 4.97,
    "first": "John",
    "last": "Doe",
    "gender": "F",
    "street": "123 Main St",
    "city": "Cityville",
    "state": "NY",
    "zip": "12345",
    "lat": 42.123,
    "long": -71.456,
    "city_pop": 12345,
    "job": "Accountant",
    "dob": "1980-01-01",
    "trans_num": "2d51696d09e0b108d7e5f9490c8abf27",
    "unix_time": 1325376018,
    "merch_lat": 42.987,
    "merch_long": -71.123
  }
}
```

Example response:
```json
{
  "prediction": 0,
  "is_fraud": false,
  "fraud_probability": 0.023,
  "transaction_id": "2d51696d09e0b108d7e5f9490c8abf27"
}
```

The API also supports batch predictions by sending multiple transactions:
```json
{
  "transactions": [
    {
      "cc_num": "2703186189652095",
      "merchant": "fraud_Rippin, Kub and Mann",
      "category": "misc_net",
      "amt": 4.97,
      "first": "John",
      "last": "Doe",
      "gender": "F",
      "street": "123 Main St",
      "city": "Cityville",
      "state": "NY",
      "zip": "12345",
      "lat": 42.123,
      "long": -71.456,
      "city_pop": 12345,
      "job": "Accountant",
      "dob": "1980-01-01",
      "trans_num": "2d51696d09e0b108d7e5f9490c8abf27",
      "unix_time": 1325376018,
      "merch_lat": 42.987,
      "merch_long": -71.123
    },
    {
      "cc_num": "2703186189652096",
      "merchant": "fraud_Rippin, Kub and Mann",
      "category": "misc_net",
      "amt": 500.00,
      "first": "Jane",
      "last": "Smith",
      "gender": "F",
      "street": "456 Oak St",
      "city": "Townsville",
      "state": "CA",
      "zip": "90210",
      "lat": 34.123,
      "long": -118.456,
      "city_pop": 3900000,
      "job": "Engineer",
      "dob": "1985-05-15",
      "trans_num": "3e51696d09e0b108d7e5f9490c8abf28",
      "unix_time": 1325376020,
      "merch_lat": 34.987,
      "merch_long": -118.123
    }
  ]
}
```
## API Usage with Preprocessed Data

The project includes a REST API for making fraud predictions using the trained model. The API expects preprocessed data in the same format as the validation dataset.

### Starting the API Server

```bash
python -m src.api.run_api
```

The API will be available at http://localhost:5001

### API Endpoints

#### Health Check
```
GET /health
```
Returns the health status of the API and whether the model is loaded.

#### Make Prediction
```
POST /predict
```

Example request body for a single transaction:
```json
{
  "transaction_data": {
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
    "amt_yeo_johnson": 0.043759851582931636
  }
}
```

Example response:
```json
{
  "prediction": 0,
  "is_fraud": false,
  "fraud_probability": 0.023,
  "transaction_id": "unknown"
}
```

The API also supports batch predictions by sending multiple transactions:
```json
{
  "transactions": [
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
      "amt_yeo_johnson": 0.043759851582931636
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
      "amt_yeo_johnson": 0.20283470583231186
    }
  ]
}
```

### Testing the API

You can test the API using the provided client example:

```bash
python -m src.client_example
```

This will send sample requests to the API and display the responses.

## Docker Setup

This project includes Docker configuration for running both the MLflow tracking server and the Fraud Detection API.

### Prerequisites

- Docker and Docker Compose installed on your system
- Git repository cloned locally

### Running with Docker Compose

1. Build and start the containers:
   ```bash
   docker compose up -d
   ```

2. Check if the services are running:
   ```bash
   docker compose ps
   ```

3. Access the services:
   - MLflow UI: http://localhost:5000
   - Fraud Detection API: http://localhost:5001/health

4. Test the API using the client example:
   ```bash
   python src/api/client_example.py
   ```

5. Stop the containers:
   ```bash
   docker compose down --remove-orphans
   ```

### API Endpoints

- `GET /health` - Health check endpoint
- `POST /predict` - Make predictions on transaction data

Example request for single prediction:
```json
{
  "transaction_data": {
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
    "amt_yeo_johnson": 0.043759851582931636
  }
}
```

Example request for batch predictions:
```json
{
  "transactions": [
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
      "amt_yeo_johnson": 0.043759851582931636
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
      "amt_yeo_johnson": 0.20283470583231186
    }
  ]
}
```
## Docker Setup (Simplified)

This project includes Docker configuration for running both the MLflow tracking server and the Fraud Detection API.

### Prerequisites

- Docker and Docker Compose installed on your system
- Git repository cloned locally

### Running with Docker Compose

1. Build and start the containers:
   ```bash
   docker compose up -d
   ```

2. Check if the services are running:
   ```bash
   docker compose ps
   ```

3. Access the services:
   - MLflow UI: http://localhost:5000
   - Fraud Detection API: http://localhost:5001/health

4. Test the API using the Docker client script:
   ```bash
   python docker-client.py
   ```

5. Stop the containers:
   ```bash
   docker compose down
   ```

### Troubleshooting

If you encounter issues with Docker Compose:

1. Make sure Docker daemon is running:
   ```bash
   systemctl status docker
   ```

2. Try restarting Docker:
   ```bash
   sudo systemctl restart docker
   ```

3. Check Docker Compose version:
   ```bash
   docker compose version
   ```

4. If you're using an older version of Docker Compose, use:
   ```bash
   docker-compose up -d
   ```
   instead of `docker compose up -d`