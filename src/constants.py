from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

import os  # noqa: E402

TRAIN_DATA_DIR = PROJECT_ROOT / "data" / "training"
PROCESSED_DATA_DIR = PROJECT_ROOT / "outputs" / "preprocessed"

EXPERIMENT_NAME = "Fraud Detection in Credit Card Transaction"
TRAIN_DATASET_FILE_NAME = PROCESSED_DATA_DIR / "train_preprocessed.csv"
TRAIN_DATASET_URL = TRAIN_DATA_DIR / "fraudTrain.csv"
VALIDATION_DATASET_URL = TRAIN_DATA_DIR / "fraudTest.csv"

VALIDATION_DATASET_FILE_NAME = PROCESSED_DATA_DIR / "validation_preprocessed.csv"

TARGET_COLUMN = "is_fraud"

MODEL_NAME = "model"  # defaulted to model it is the name of the model after deployment
MLFLOW_URI = os.environ.get("MLFLOW_URI", "http://127.0.0.1:5000/")
MLFLOW_MODEL_URI = os.environ.get(
    "MLFLOW_MODEL_URI", "/home/ezdonka/repos/BTH-ML/ml-engineering-cc-fraud-detection/outputs"
)
