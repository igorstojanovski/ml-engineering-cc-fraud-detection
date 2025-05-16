from src.libs.preprocessorLib import FraudDetectionConfig, main
import src.constants

# Define your parameters
params = {
    "ds_url": src.constants.VALIDATION_DATASET_URL,
    "output_filename": src.constants.VALIDATION_DATASET_FILE_NAME,
    "context": src.constants.VALIDATION_RUN_NAME,
    "name": "Fraud Detection in Credit Card Transactions - Validation Data Set / Preprocessed"
}

# Create config object with your parameters
config = FraudDetectionConfig(**params)

# Run the preprocessing
main(config)
