from src.libs.preprocessorLib import FraudDetectionConfig, main
import src.constants

# Define your parameters
params = {
    "ds_url": src.constants.TRAIN_DATASET_URL,
    "output_filename": src.constants.TRAIN_DATASET_FILE_NAME,
    "context": "training",
    "name": "Fraud Detection in Credit Card Transactions - Training Data Set / Preprocessed"
}

# Create config object with your parameters
config = FraudDetectionConfig(**params)

# Run the preprocessing
main(config)
