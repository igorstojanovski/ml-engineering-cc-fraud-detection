import unittest

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

import os
import sys
import pickle

# Add the project root to the path to ensure correct imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.constants import TARGET_COLUMN, TRAIN_DATASET_FILE_NAME
from src.libs.libs import SMOTESampler


class TestNoiseSensitivity(unittest.TestCase):
    """Test class to evaluate model robustness against input noise."""

    @classmethod
    def setUpClass(cls):
        """Set up test data and model once for all test methods."""
        # Load the model
        cls.model = cls.load_model()

        # Load into DataFrame
        cls.train_preprocessed = pd.read_csv(TRAIN_DATASET_FILE_NAME)

        # Apply SMOTE
        smote_sampler = SMOTESampler(target_column=TARGET_COLUMN)
        cls.smote_resampled_df = smote_sampler.fit_resample(cls.train_preprocessed)
        print("SMOTE completed for train data")

        # Select feature columns (independent variables) from the training data
        cls.X_train_smote = cls.smote_resampled_df.drop(columns=TARGET_COLUMN, axis=1)

        # Select target columns (dependent variables) from the training data
        cls.y_train_smote = cls.smote_resampled_df[TARGET_COLUMN]

        # Split data into train and test sets
        cls.X_train, cls.X_test, cls.y_train, cls.y_test = train_test_split(
            cls.X_train_smote, cls.y_train_smote, test_size=0.3, random_state=42
        )

        # Get baseline performance (no noise)
        cls.baseline_predictions = cls.model.predict(cls.X_test)
        cls.baseline_f1 = f1_score(cls.y_test, cls.baseline_predictions)
        cls.baseline_accuracy = accuracy_score(cls.y_test, cls.baseline_predictions)
        cls.baseline_precision = precision_score(cls.y_test, cls.baseline_predictions)
        cls.baseline_recall = recall_score(cls.y_test, cls.baseline_predictions)

        print("\nBaseline Performance (No Noise):")
        print(f"F1 Score: {cls.baseline_f1:.4f}")
        print(f"Accuracy: {cls.baseline_accuracy:.4f}")
        print(f"Precision: {cls.baseline_precision:.4f}")
        print(f"Recall: {cls.baseline_recall:.4f}")

    @staticmethod
    def load_model():
        model_uri = "outputs/models/model.pkl"
        with open(model_uri, "rb") as f:
            model = pickle.load(f)
        return model

    @staticmethod
    def add_gaussian_noise(X, std_dev=0.1):
        """Add Gaussian noise to the input data.

        Args:
            X: Input data
            std_dev: Standard deviation of the noise

        Returns:
            DataFrame with added noise
        """
        # Create a copy to avoid modifying the original data
        X_noisy = X.copy()

        # Only add noise to numeric columns
        numeric_cols = X_noisy.select_dtypes(include=np.number).columns

        for col in numeric_cols:
            noise = np.random.normal(0, std_dev, X_noisy[col].shape)
            X_noisy[col] = X_noisy[col] + noise

        return X_noisy

    def test_noise_sensitivity_f1_score(self):
        """Test model robustness against different levels of noise using F1 score."""
        # Define noise levels to test
        noise_levels = [0.01, 0.05, 0.1, 0.2, 0.5]

        # Define minimum acceptable performance as percentage of baseline
        min_acceptable_performance = 0.8  # 80% of baseline performance

        print("\nNoise Sensitivity Test - F1 Score:")
        print("-" * 60)
        print(
            f"{'Noise Level':<15} {'F1 Score':<15} {'% of Baseline':<15} {'Result':<10}"
        )
        print("-" * 60)

        # Test each noise level
        for noise_level in noise_levels:
            # Add noise to test data
            X_noisy = self.add_gaussian_noise(self.X_test, std_dev=noise_level)

            # Make predictions
            y_pred = self.model.predict(X_noisy)

            # Calculate F1 score
            f1 = f1_score(self.y_test, y_pred)

            # Calculate percentage of baseline
            percentage = (f1 / self.baseline_f1) * 100

            # Determine result
            result = (
                "PASS" if percentage >= min_acceptable_performance * 100 else "FAIL"
            )

            print(f"{noise_level:<15.2f} {f1:<15.4f} {percentage:<15.2f}% {result:<10}")

            # Assert that performance is above minimum acceptable level
            self.assertGreaterEqual(
                percentage,
                min_acceptable_performance * 100,
                f"Model performance with noise level {noise_level} dropped below "
                f"{min_acceptable_performance * 100}% of baseline",
            )

        print("-" * 60)

    def test_noise_sensitivity_all_metrics(self):
        """Test model robustness against different levels of noise using multiple metrics."""
        # Define noise levels to test
        noise_levels = [0.01, 0.05, 0.1, 0.2]

        # Define minimum acceptable performance as percentage of baseline
        min_acceptable_performance = 0.8  # 80% of baseline performance

        print("\nNoise Sensitivity Test - All Metrics:")
        print("-" * 80)
        print(
            f"{'Noise':<8} "
            f"{'F1 Score':<20} "
            f"{'Accuracy':<20} "
            f"{'Precision':<20} "
            f"{'Recall':<20}"
        )
        print(
            f"{'Level':<8} "
            f"{'Score (% Base)':<20} "
            f"{'Score (% Base)':<20} "
            f"{'Score (% Base)':<20} "
            f"{'Score (% Base)':<20}"
        )
        print("-" * 80)

        # Store results for reporting
        failed_tests = []

        # Test each noise level
        for noise_level in noise_levels:
            # Add noise to test data
            X_noisy = self.add_gaussian_noise(self.X_test, std_dev=noise_level)

            # Make predictions
            y_pred = self.model.predict(X_noisy)

            # Calculate metrics
            f1 = f1_score(self.y_test, y_pred)
            accuracy = accuracy_score(self.y_test, y_pred)
            precision = precision_score(self.y_test, y_pred)
            recall = recall_score(self.y_test, y_pred)

            # Calculate percentages of baseline
            f1_pct = (f1 / self.baseline_f1) * 100
            acc_pct = (accuracy / self.baseline_accuracy) * 100
            prec_pct = (precision / self.baseline_precision) * 100
            rec_pct = (recall / self.baseline_recall) * 100

            # Print results
            print(
                f"{noise_level:<8.2f} {f1:.4f} ({f1_pct:.1f}%) {accuracy:.4f} ({acc_pct:.1f}%) "
                f"{precision:.4f} ({prec_pct:.1f}%) {recall:.4f} ({rec_pct:.1f}%)"
            )

            # Check if any metric falls below acceptable level
            metrics = [
                ("F1", f1_pct),
                ("Accuracy", acc_pct),
                ("Precision", prec_pct),
                ("Recall", rec_pct),
            ]

            for metric_name, percentage in metrics:
                if percentage < min_acceptable_performance * 100:
                    failed_tests.append((noise_level, metric_name, percentage))

        print("-" * 80)

        # Assert that all metrics are above minimum acceptable level
        if failed_tests:
            failure_message = "\nModel performance degraded below acceptable levels:\n"
            for noise, metric, percentage in failed_tests:
                failure_message += (
                    f"  - Noise level {noise}: {metric} "
                    f"dropped to {percentage:.1f}% of baseline\n"
                )

            self.fail(failure_message)

    def test_feature_specific_noise_sensitivity(self):
        """Test model sensitivity to noise in specific features."""
        # Select important features to test individually
        # You can replace these with the most important features for your model
        important_features = self.X_test.columns[:5]  # Testing first 5 features

        noise_level = 0.2  # Higher noise level for individual features
        min_acceptable_performance = 0.9  # 90% of baseline

        print("\nFeature-Specific Noise Sensitivity Test:")
        print("-" * 70)
        print(f"{'Feature':<30} {'F1 Score':<15} {'% of Baseline':<15} {'Result':<10}")
        print("-" * 70)

        for feature in important_features:
            # Create a copy of test data
            X_feature_noisy = self.X_test.copy()

            # Only add noise to the specific feature if it's numeric
            if np.issubdtype(X_feature_noisy[feature].dtype, np.number):
                noise = np.random.normal(0, noise_level, X_feature_noisy[feature].shape)
                X_feature_noisy[feature] = X_feature_noisy[feature] + noise

                # Make predictions
                y_pred = self.model.predict(X_feature_noisy)

                # Calculate F1 score
                f1 = f1_score(self.y_test, y_pred)

                # Calculate percentage of baseline
                percentage = (f1 / self.baseline_f1) * 100

                # Determine result
                result = (
                    "PASS" if percentage >= min_acceptable_performance * 100 else "FAIL"
                )

                print(f"{feature:<30} {f1:<15.4f} {percentage:<15.2f}% {result:<10}")

                # No assertion here - this is informational to identify sensitive
                # features
            else:
                print(f"{feature:<30} {'N/A':<15} {'N/A':<15} {'SKIPPED':<10}")


if __name__ == "__main__":
    unittest.main()
