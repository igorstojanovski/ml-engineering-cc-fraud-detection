from src import constants
from src.libs.preprocessorLib import FraudDetectionConfig, main

# Define your parameters
params = {
    "ds_url": constants.TRAIN_DATASET_URL,
    "output_filename": constants.TRAIN_DATASET_FILE_NAME,
    "context": "training",
    "name": "Fraud Detection in Credit Card Transactions - Training Data Set / Preprocessed",
}

# Create config object with your parameters
config = FraudDetectionConfig(**params)

# Run the preprocessing
main(config)
