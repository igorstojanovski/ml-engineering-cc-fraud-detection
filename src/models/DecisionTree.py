import mlflow
import mlflow.sklearn  

import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    )
from src.libs.libs import *

import warnings
warnings.filterwarnings('ignore')

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import tempfile
import os
import src.constants
from mlflow.models.signature import infer_signature
from sklearn.model_selection import GridSearchCV
from src.constants import TARGET_COLUMN, DATA_URI



mlflow.set_tracking_uri(uri=src.constants.ML_FLOW_URI)
mlflow.set_experiment(src.constants.EXPERIMENT_NAME)
# Load the dataset
with mlflow.start_run(run_name="decision_tree_experiment") as run:
    mlflow.artifacts.download_artifacts(DATA_URI, dst_path="./downloaded_artifacts")

    # Load into DataFrame
    train_preprocessed = pd.read_csv("train_preprocessed.csv")

    # Apply SMOTE
    smote_sampler = SMOTESampler(target_column=TARGET_COLUMN)
    smote_resampled_df = smote_sampler.fit_resample(train_preprocessed)
    print(f"SMOTE completed for train data")

    # Select feature columns (independent variables) from the training data to create the training set
    X_train_smote = smote_resampled_df.drop(columns=TARGET_COLUMN, axis=1)

    # Select target columns (dependent variables) from the training data to create the target set 
    y_train_smote = smote_resampled_df[TARGET_COLUMN]
    # random_state=42 to ensure reproducibility
    X_train, X_test, y_train, y_test = train_test_split(X_train_smote, y_train_smote, test_size=0.3, random_state=42)

    # Train model
    dt_model = DecisionTreeClassifier(random_state=42)

    # Define the hyperparameter grid
    param_grid = {
        "criterion": ["gini", "entropy"],  
        "max_depth": [20, 30],  
        "min_samples_split": [2, 5], 
        "min_samples_leaf": [1, 2], 
        "max_features": ["sqrt"]
    }

    # Create the grid search object
    grid_search = GridSearchCV(
        estimator=dt_model,
        param_grid=param_grid,
        cv=3,  # 5-fold cross-validation
        scoring='f1',  # or 'f1', 'roc_auc', etc.
        n_jobs=-1,  # Use all processors
        verbose=0
    )

    # Fit to your training data
    # training
    grid_search.fit(X_train, y_train)
    best_model = grid_search.best_estimator_

    # prediction
    test_prediction = best_model.predict(X_test)
    train_prediction = best_model.predict(X_train)

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

    mlflow.log_metric("true_positive", true_positive)
    mlflow.log_metric("true_negative", true_negative)
    mlflow.log_metric("false_positive", false_positive)
    mlflow.log_metric("false_negative", false_negative)

    train_precision_pos_class = precision_score(y_train, train_prediction, pos_label=1, zero_division=0)
    test_precision_pos_class = precision_score(y_test, test_prediction, pos_label=1, zero_division=0)

    train_recall_pos_class = recall_score(y_train, train_prediction, pos_label=1, zero_division=0)
    test_recall_pos_class = recall_score(y_test, test_prediction, pos_label=1, zero_division=0)

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
    mlflow.sklearn.log_model(best_model, signature=signature, input_example=X_train, artifact_path="model")
    mlflow.end_run()

test_score = accuracy_score(y_test, best_model.predict(X_test)) * 100
train_score = accuracy_score(y_train_smote, best_model.predict(X_train_smote)) * 100

print_score(best_model, X_train_smote, y_train_smote, X_test, y_test, train=True)
print_score(best_model, X_train_smote, y_train_smote, X_test, y_test, train=False)
