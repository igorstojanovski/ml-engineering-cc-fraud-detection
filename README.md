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

The API supports both raw transaction data and preprocessed data.

##### Using Raw Transaction Data

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

##### Using Preprocessed Data

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

You can test the API using the provided client examples:

```bash
# Test with preprocessed data
python -m src.api.client_example

# Test with raw transaction data
python -m src.api.raw_data_example
```

These will send sample requests to the API and display the responses.

## Running locally with Docker Compose

This project uses `docker-compose` to serve the production-ready frontend through Nginx, with proxying of `/api/*` requests to a locally running ML model.

-  ⚠️ The `model` service is not included in this setup yet.  
- For now, make sure your ML API is running on your host machine at `localhost:5001`.  
- In the future, this will be replaced with a dedicated `model` service.

To run the frontend + proxy setup locally:

```bash
docker compose up --build
```

then open your browser at http://localhost:3000