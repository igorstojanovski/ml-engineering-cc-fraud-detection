import os
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
import mlflow
import mlflow.sklearn
from src.constants import ML_FLOW_URI, MODEL_URI
from src.libs.preprocessorLib import FraudDetectionConfig, create_preprocessing_pipeline

# Initialize Flask app
app = Flask(__name__)

# Set MLflow tracking URI
mlflow.set_tracking_uri(uri=ML_FLOW_URI)

# Load the model at startup
def load_model():
    """
    Load the best model from MLflow model registry
    """
    model_uri = MODEL_URI
    model = mlflow.sklearn.load_model(model_uri)
    return model

# Load model at startup
model = load_model()

@app.route('/', methods=['GET'])
def get():
    return jsonify({"message": "API is up and running!"})

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    if model is not None:
        return jsonify({"status": "healthy", "model_loaded": True})
    return jsonify({"status": "unhealthy", "model_loaded": False}), 503

@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint to make fraud predictions on transaction data
    
    Expected JSON format:
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
    
    Or for batch predictions:
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
    """
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500
    
    try:
        # Get data from request
        data = request.json
        
        # Check if it's a single transaction or batch
        if "transaction_data" in data:
            # Single transaction
            transaction = data["transaction_data"]
            df = pd.DataFrame([transaction])
            
            # Preprocess the data (same preprocessing as in training)
            df = preprocess_data(df)
            
            # Make prediction
            prediction = model.predict(df)
            probability = model.predict_proba(df)[:, 1]  # Probability of fraud class
            
            result = {
                "prediction": int(prediction[0]),  # 0: not fraud, 1: fraud
                "is_fraud": bool(prediction[0]),
                "fraud_probability": float(probability[0]),
                "transaction_id": transaction.get("trans_num", "unknown")
            }
            
            return jsonify(result)
            
        elif "transactions" in data:
            # Batch processing
            transactions = data["transactions"]
            df = pd.DataFrame(transactions)
            
            # Preprocess the data
            df = preprocess_data(df)
            
            # Make predictions
            predictions = model.predict(df)
            probabilities = model.predict_proba(df)[:, 1]
            
            results = []
            for i, transaction in enumerate(transactions):
                results.append({
                    "prediction": int(predictions[i]),
                    "is_fraud": bool(predictions[i]),
                    "fraud_probability": float(probabilities[i]),
                    "transaction_id": transaction.get("trans_num", f"unknown_{i}")
                })
            
            return jsonify({"results": results})
        
        else:
            return jsonify({"error": "Invalid request format"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def preprocess_data(df):
    """
    Preprocess the input data to match the format expected by the model
    
    For the preprocessed data, we expect the following features:
    - category
    - gender
    - transaction_hour
    - transaction_month
    - is_weekend
    - day_of_week
    - part_of_day
    - age
    - distance
    - city_pop_bin
    - amt_yeo_johnson
    """
    try:
        # Check if data is already preprocessed
        required_columns = [
            'category', 'gender', 'transaction_hour', 'transaction_month',
            'is_weekend', 'day_of_week', 'part_of_day', 'age',
            'distance', 'city_pop_bin', 'amt_yeo_johnson'
        ]
        
        # If all required columns are present, data is already preprocessed
        if all(col in df.columns for col in required_columns):
            processed_df = df[required_columns].copy()
            
            # Convert data types to match what the model expects
            for col in processed_df.columns:
                processed_df[col] = processed_df[col].astype(float)
                
            print(f"Using already preprocessed data with shape: {processed_df.shape}")
            return processed_df
        
        # If raw data, apply preprocessing pipeline
        print("Applying preprocessing pipeline to raw data")
        
        # Create config with default values
        config = FraudDetectionConfig(
            ds_url="",  # Not needed as we're not loading from file
            output_filename="",  # Not saving to file
            context="api",
            name="API Prediction"
        )
        
        # Create and apply preprocessing pipeline
        preprocessor = create_preprocessing_pipeline(config)
        
        # Fit and transform the data
        preprocessor.fit(df)
        processed_df = preprocessor.transform(df)
        
        print(f"Preprocessed data shape: {processed_df.shape}")
        return processed_df
        
    except Exception as e:
        print(f"Error in preprocessing: {e}")
        raise

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

if __name__ == '__main__':
    # Run the Flask app
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)