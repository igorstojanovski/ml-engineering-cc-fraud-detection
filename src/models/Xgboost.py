import json
import os
import sys
import tempfile
import warnings

import matplotlib.pyplot as plt
import mlflow.sklearn
import pandas as pd
import seaborn as sns
from mlflow.models.signature import infer_signature
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import GridSearchCV, train_test_split
from xgboost import XGBClassifier

# Add the project root to the path to ensure correct imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.constants import (
    EXPERIMENT_NAME,
    MLFLOW_URI,
    TARGET_COLUMN,
    TRAIN_DATASET_FILE_NAME,
)
from src.libs.libs import SMOTESampler

warnings.filterwarnings("ignore")


mlflow.set_tracking_uri(uri=MLFLOW_URI)

mlflow.set_experiment(EXPERIMENT_NAME)


train_preprocessed = pd.read_csv(TRAIN_DATASET_FILE_NAME)

# Apply SMOTE
smote_sampler = SMOTESampler(target_column=TARGET_COLUMN)
smote_resampled_df = smote_sampler.fit_resample(train_preprocessed)
print("SMOTE completed for train data")

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

# Train model
xgb_model = XGBClassifier(n_jobs=-1, tree_method="hist", early_stopping_rounds=10)

param_grid = {
    "n_estimators": [100],
    "learning_rate": [0.1],
    "max_depth": [6],
    "min_child_weight": [3],
    "subsample": [0.8],
    "colsample_bytree": [0.8],
    "gamma": [0.1],
}

# Create the grid search object
grid_search = GridSearchCV(
    estimator=xgb_model,
    param_grid=param_grid,
    cv=3,  # 3-fold cross-validation
    scoring="f1",
    n_jobs=-1,  # Use all processors
    verbose=0,
)

# Fit to your training data
grid_search.fit(X_train, y_train, eval_set=[(X_test, y_test)])
best_model = grid_search.best_estimator_

# prediction
test_prediction = best_model.predict(X_test)

signature = infer_signature(X_test, test_prediction)
report = classification_report(
    y_test, test_prediction, zero_division=0, output_dict=True
)
print(classification_report(y_test, test_prediction, zero_division=0))

with mlflow.start_run(run_name="Xgboost_experiment") as run:
    mlflow.log_params(grid_search.best_params_)  # Logs best combo
    mlflow.log_metric("best_cv_score", grid_search.best_score_)

    # Step 1: get confusion matrix values
    conf_matrix = confusion_matrix(y_test, test_prediction)
    true_positive = conf_matrix[0][0]
    true_negative = conf_matrix[1][1]
    false_positive = conf_matrix[0][1]
    false_negative = conf_matrix[1][0]

    mlflow.log_metric("true_positive", true_positive)
    mlflow.log_metric("true_negative", true_negative)
    mlflow.log_metric("false_positive", false_positive)
    mlflow.log_metric("false_negative", false_negative)

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

    # Log model
    mlflow.sklearn.log_model(best_model, signature=signature, artifact_path="model")

    # Log each class's metrics
    for label, metrics in report.items():
        # Skip 'accuracy', 'macro avg', 'weighted avg' for this loop
        if label in ["accuracy", "macro avg", "weighted avg"]:
            continue
        for metric_name, value in metrics.items():
            mlflow.log_metric(f"{label}_{metric_name}", value)

    mlflow.log_metric("accuracy", report["accuracy"])
    for avg_type in ["macro avg", "weighted avg"]:
        for metric_name, value in report[avg_type].items():
            mlflow.log_metric(f"{avg_type.replace(' ', '_')}_{metric_name}", value)

    with open("classification_report.json", "w") as f:
        json.dump(report, f, indent=4)
    mlflow.log_artifact("classification_report.json")

    mlflow.end_run()
