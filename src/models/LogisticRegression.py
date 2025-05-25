# ⚙️ Standard library
import json
import os
import pickle
import tempfile
import warnings
from multiprocessing import cpu_count
from pathlib import Path

# 🛠️ Parallelism and memory control
import joblib
import matplotlib.pyplot as plt
# 🧠 MLflow
import mlflow
import mlflow.sklearn
import numpy as np
# 📊 Data and plotting
import pandas as pd
import seaborn as sns
from mlflow.models.signature import infer_signature
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, f1_score, precision_score,
                             recall_score)
# 🤖 Machine learning
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline

# 🧩 Project-specific
from src.constants import (DATA_URI, EXPERIMENT_NAME, ML_FLOW_URI,
                           TARGET_COLUMN, TRAIN_DATASET_FILE_NAME)
from src.libs.libs import *

# 🔇 Suppress warnings
warnings.filterwarnings("ignore")


# Choose a safe temp folder regardless of OS
joblib_temp = os.getenv("JOBLIB_TEMP_FOLDER", tempfile.gettempdir())

# Optional: place joblib temp files under a subdir so they don’t mix with
# other temp files
joblib_temp = Path(joblib_temp) / "joblib_tmp"
joblib_temp.mkdir(parents=True, exist_ok=True)

os.environ["JOBLIB_TEMP_FOLDER"] = str(joblib_temp)

# Use parallel backend
joblib.parallel_backend("loky")

mlflow.set_tracking_uri(uri=ML_FLOW_URI)
# start it on console with:
# mlflow server --host 127.0.0.1 --port 8080

# MLflow Experiment
mlflow.set_experiment(EXPERIMENT_NAME)
# Load the dataset
with mlflow.start_run(run_name="logistic_regression_experiment") as run:
    # Load the artifact from the current run or another run
    # mlflow.artifacts.download_artifacts(DATA_URI, dst_path="./downloaded_artifacts")

    # Load into DataFrame
    train_preprocessed = pd.read_csv(TRAIN_DATASET_FILE_NAME)

    random_state = 15

    # Apply SMOTE
    smote_sampler = SMOTESampler(target_column=TARGET_COLUMN)
    smote_resampled_df = smote_sampler.fit_resample(train_preprocessed)
    print(f"SMOTE completed for train data")

    # Select feature columns (independent variables) from the training data to
    # create the training set
    X_train_smote = smote_resampled_df.drop(columns=TARGET_COLUMN, axis=1)

    # Select target columns (dependent variables) from the training data to
    # create the target set
    y_train_smote = smote_resampled_df[TARGET_COLUMN]

    # random_state=42 to ensure reproducibility
    X_train, X_test, y_train, y_test = train_test_split(
        X_train_smote, y_train_smote, test_size=0.3, random_state=42
    )
    # 1. Logistic Regression
    # Train model
    params_grid = {
        "penalty": ["l1", "l2", "elasticnet", None],
        "C": [0.01, 0.1, 1, 10, 100],
        "solver": ["lbfgs", "saga", "liblinear"],
        "max_iter": [100, 200, 500],
    }

    lr_model = LogisticRegression(solver="liblinear")
    safe_jobs = max(1, cpu_count() - 2)
    grid_search = GridSearchCV(
        estimator=lr_model,
        param_grid=params_grid,
        cv=3,
        n_jobs=safe_jobs,
        scoring="f1",  # Use F1 score for classification optimization
    )
    grid_search.fit(X_train, y_train)
    best_model = grid_search.best_estimator_

    # prediction
    train_prediction = best_model.predict(X_train)
    test_prediction = best_model.predict(X_test)

    report = classification_report(y_test, test_prediction)

    signature = infer_signature(X_test, test_prediction)

    # Evaluate
    f1 = f1_score(y_test, test_prediction)
    precision = precision_score(y_test, test_prediction)
    recall = recall_score(y_test, test_prediction)
    acc = accuracy_score(y_test, test_prediction)

    mlflow.log_params(grid_search.best_params_)  # Logs best combo
    mlflow.log_metric("best_cv_score", grid_search.best_score_)

    # Step 1: get confusion matrix values
    conf_matrix = confusion_matrix(y_test, test_prediction)
    true_positive = conf_matrix[0][0]
    true_negative = conf_matrix[1][1]
    false_positive = conf_matrix[0][1]
    false_negative = conf_matrix[1][0]

    train_precision_pos_class = precision_score(
        y_train, train_prediction, pos_label=1, zero_division=0
    )
    test_precision_pos_class = precision_score(
        y_test, test_prediction, pos_label=1, zero_division=0
    )

    train_recall_pos_class = recall_score(
        y_train, train_prediction, pos_label=1, zero_division=0
    )
    test_recall_pos_class = recall_score(
        y_test, test_prediction, pos_label=1, zero_division=0
    )

    mlflow.log_metric("true_positive", true_positive)
    mlflow.log_metric("true_negative", true_negative)
    mlflow.log_metric("false_positive", false_positive)
    mlflow.log_metric("false_negative", false_negative)
    mlflow.log_metric("recall on class fraud for train dataset", train_recall_pos_class)
    mlflow.log_metric("recall on class fraud for test dataset", test_recall_pos_class)

    # Step 2: Plot it using seaborn
    plt.figure(figsize=(6, 4))
    sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix")

    # Step 3: Save it temporarily
    with tempfile.TemporaryDirectory() as tmp_dir:
        cm_path = os.path.join(tmp_dir, "confusion_matrix.png")
        plt.savefig(cm_path)
        plt.close()
        # Step 4: Log to MLflow
        mlflow.log_artifact(cm_path, artifact_path="plots")

    mlflow.log_metric("f1", f1)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    mlflow.log_metric("accuracy", acc)

    # Log model
    mlflow.sklearn.log_model(best_model, signature=signature, artifact_path="model")

    mlflow.end_run()

test_score = accuracy_score(y_test, best_model.predict(X_test)) * 100
train_score = accuracy_score(y_train_smote, best_model.predict(X_train_smote)) * 100


print_score(best_model, X_train_smote, y_train_smote, X_test, y_test, train=True)
print_score(best_model, X_train_smote, y_train_smote, X_test, y_test, train=False)

# Save the trained model as a .pkl file for DVC to track
with open("outputs/models/logistic_model.pkl", "wb") as f:
    pickle.dump(best_model, f)

# Save metrics to a JSON file for DVC to track
metrics = {
    "f1": float(f1),
    "precision": float(precision),
    "recall": float(recall),
    "accuracy": float(acc),
    "true_positive": int(true_positive),
    "true_negative": int(true_negative),
    "false_positive": int(false_positive),
    "false_negative": int(false_negative),
    "recall_train_fraud": float(train_recall_pos_class),
    "recall_test_fraud": float(test_recall_pos_class),
    "train_score": float(train_score),
    "test_score": float(test_score),
}

with open("outputs/metrics/logistic_metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)
