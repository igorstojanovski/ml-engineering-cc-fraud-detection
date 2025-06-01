import os
import sys

# Add the project root to the path to ensure correct imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

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
