from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

TRAIN_DATA_DIR = PROJECT_ROOT / "data" / "training"
PROCESSED_DATA_DIR = PROJECT_ROOT / "outputs" / "preprocessed"


EXPERIMENT_NAME = "Fraud Detection in Credit Card Transaction"
TRAIN_DATASET_FILE_NAME = PROCESSED_DATA_DIR / "train_preprocessed.csv"
TRAIN_DATASET_URL = TRAIN_DATA_DIR / "fraudTrain.csv"
VALIDATION_DATASET_URL = TRAIN_DATA_DIR / "fraudTest.csv"
BEST_MODEL_RUN_ID = "359dfc339a5541ba830ade905ec0b27b"
BEST_MODEL_NAME = "Decision Tree"

VALIDATION_DATASET_FILE_NAME = PROCESSED_DATA_DIR / "validation_preprocessed.csv"

TRAINING_RUN_NAME = "training"
VALIDATION_RUN_NAME = "validation"

MODEL_URI = "mlartifacts/282047854241216555/359dfc339a5541ba830ade905ec0b27b/artifacts/model/"
DATA_URI = "mlartifacts/282047854241216555/d3237dabc0064c7e97698fa56adba180/artifacts/train_preprocessed.csv"

TARGET_COLUMN = 'is_fraud'

ML_FLOW_URI = "http://127.0.0.1:5000/"
