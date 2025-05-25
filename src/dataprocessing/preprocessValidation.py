from src.libs.preprocessorLib import FraudDetectionConfig, main
from src import constants

# Define your parameters
params = {
    "ds_url": constants.VALIDATION_DATASET_URL,
    "output_filename": constants.VALIDATION_DATASET_FILE_NAME,
    "context": "Validation",
    "name": "Fraud Detection in Credit Card Transactions - Validation Data Set / Preprocessed",
}

# Create config object with your parameters
config = FraudDetectionConfig(**params)

# Run the preprocessing
main(config)
