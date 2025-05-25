import unittest
import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, precision_score, recall_score
from src.constants import MODEL_URI, TARGET_COLUMN
from src.libs.libs import SMOTESampler
from fairlearn.metrics import MetricFrame, selection_rate, true_positive_rate, false_positive_rate


class TestFairnessAndBias(unittest.TestCase):
    """Test class to evaluate model fairness and bias across sensitive features."""

    @classmethod
    def setUpClass(cls):
        """Set up test data and model once for all test methods."""
        # Load the model
        cls.model_uri = MODEL_URI
        cls.model = mlflow.sklearn.load_model(cls.model_uri)

        # Load into DataFrame
        cls.train_preprocessed = pd.read_csv("train_preprocessed.csv")

        # Apply SMOTE
        smote_sampler = SMOTESampler(target_column=TARGET_COLUMN)
        cls.smote_resampled_df = smote_sampler.fit_resample(cls.train_preprocessed)
        print(f"SMOTE completed for train data")

        # Select feature columns (independent variables) from the training data
        cls.X_train_smote = cls.smote_resampled_df.drop(columns=TARGET_COLUMN, axis=1)

        # Select target columns (dependent variables) from the training data
        cls.y_train_smote = cls.smote_resampled_df[TARGET_COLUMN]

        # Split data into train and test sets
        cls.X_train, cls.X_test, cls.y_train, cls.y_test = train_test_split(
            cls.X_train_smote, cls.y_train_smote, test_size=0.3, random_state=42
        )

        # Generate predictions
        cls.y_pred = cls.model.predict(cls.X_test)

        # Define sensitive features to test
        cls.sensitive_features = ['gender']

        # Define acceptable thresholds for fairness
        cls.max_disparity_threshold = 0.2  # Maximum allowed disparity (20%)
        cls.min_performance_threshold = 0.7  # Minimum performance for any group (70%)

    def test_performance_parity_across_groups(self):
        """Test that model performance is similar across different demographic groups."""
        for sensitive_column in self.sensitive_features:
            # Skip if sensitive column doesn't exist
            if sensitive_column not in self.X_test.columns:
                print(
                    f"Warning: Sensitive column '{sensitive_column}' not found in dataset. Skipping.")
                continue

            sensitive_values = self.X_test[sensitive_column]

            # Calculate metrics for each group
            results = []
            for group in sensitive_values.unique():
                group_mask = sensitive_values == group
                group_y_true = self.y_test[group_mask]
                group_y_pred = self.y_pred[group_mask]

                # Skip groups with too few samples
                if sum(group_mask) < 10:
                    print(
                        f"Warning: Group '{group}' in '{sensitive_column}' has fewer than 10 samples. Skipping.")
                    continue

                results.append({
                    'Group': group,
                    'Count': group_mask.sum(),
                    'Precision': precision_score(group_y_true, group_y_pred),
                    'Recall': recall_score(group_y_true, group_y_pred),
                    'F1': f1_score(group_y_true, group_y_pred)
                })

            # Convert to DataFrame for easier analysis
            df_results = pd.DataFrame(results)
            print(f"\nPerformance metrics across {sensitive_column} groups:")
            print(df_results)

            # Calculate disparities
            max_precision = df_results['Precision'].max()
            min_precision = df_results['Precision'].min()
            precision_disparity = max_precision - min_precision

            max_recall = df_results['Recall'].max()
            min_recall = df_results['Recall'].min()
            recall_disparity = max_recall - min_recall

            max_f1 = df_results['F1'].max()
            min_f1 = df_results['F1'].min()
            f1_disparity = max_f1 - min_f1

            print(f"\nDisparities for {sensitive_column}:")
            print(f"Precision disparity: {precision_disparity:.4f}")
            print(f"Recall disparity: {recall_disparity:.4f}")
            print(f"F1 disparity: {f1_disparity:.4f}")

            # Assert that disparities are below threshold
            self.assertLessEqual(
                precision_disparity,
                self.max_disparity_threshold,
                f"Precision disparity for {sensitive_column} exceeds threshold: {
                    precision_disparity:.4f}"
            )

            self.assertLessEqual(
                recall_disparity,
                self.max_disparity_threshold,
                f"Recall disparity for {sensitive_column} exceeds threshold: {
                    recall_disparity:.4f}"
            )

            self.assertLessEqual(
                f1_disparity,
                self.max_disparity_threshold,
                f"F1 disparity for {sensitive_column} exceeds threshold: {
                    f1_disparity:.4f}"
            )

            # Assert minimum performance for all groups
            self.assertGreaterEqual(
                min_precision,
                self.min_performance_threshold,
                f"Minimum precision across {sensitive_column} groups below threshold: {
                    min_precision:.4f}"
            )

            self.assertGreaterEqual(
                min_recall,
                self.min_performance_threshold,
                f"Minimum recall across {sensitive_column} groups below threshold: {
                    min_recall:.4f}"
            )

            self.assertGreaterEqual(
                min_f1,
                self.min_performance_threshold,
                f"Minimum F1 across {sensitive_column} groups below threshold: {
                    min_f1:.4f}"
            )

    def test_fairlearn_metrics(self):
        """Test fairness using Fairlearn metrics."""
        for sensitive_column in self.sensitive_features:
            # Skip if sensitive column doesn't exist
            if sensitive_column not in self.X_test.columns:
                print(
                    f"Warning: Sensitive column '{sensitive_column}' not found in dataset. Skipping.")
                continue

            sensitive_values = self.X_test[sensitive_column]

            # Create metric frame
            metric_frame = MetricFrame(
                metrics={
                    "selection_rate": selection_rate,
                    "true_positive_rate": true_positive_rate,
                    "false_positive_rate": false_positive_rate
                },
                y_true=self.y_test,
                y_pred=self.y_pred,
                sensitive_features=sensitive_values
            )

            # Print metrics by group
            print(f"\nFairlearn metrics across {sensitive_column} groups:")
            print(metric_frame.by_group)

            # Calculate disparities
            selection_rate_disparity = metric_frame.difference(
                method="between_groups")["selection_rate"]
            tpr_disparity = metric_frame.difference(method="between_groups")[
                "true_positive_rate"]
            fpr_disparity = metric_frame.difference(method="between_groups")[
                "false_positive_rate"]

            print(f"\nFairlearn disparities for {sensitive_column}:")
            print(f"Selection rate disparity: {selection_rate_disparity:.4f}")
            print(f"True positive rate disparity: {tpr_disparity:.4f}")
            print(f"False positive rate disparity: {fpr_disparity:.4f}")

            # Assert that disparities are below threshold
            self.assertLessEqual(
                selection_rate_disparity,
                self.max_disparity_threshold,
                f"Selection rate disparity for {sensitive_column} exceeds threshold: {
                    selection_rate_disparity:.4f}"
            )

            self.assertLessEqual(
                tpr_disparity,
                self.max_disparity_threshold,
                f"True positive rate disparity for {sensitive_column} exceeds threshold: {
                    tpr_disparity:.4f}"
            )

            self.assertLessEqual(
                fpr_disparity,
                self.max_disparity_threshold,
                f"False positive rate disparity for {sensitive_column} exceeds threshold: {
                    fpr_disparity:.4f}"
            )

    def test_demographic_parity(self):
        """Test for demographic parity (equal selection rates across groups)."""
        for sensitive_column in self.sensitive_features:
            # Skip if sensitive column doesn't exist
            if sensitive_column not in self.X_test.columns:
                print(
                    f"Warning: Sensitive column '{sensitive_column}' not found in dataset. Skipping.")
                continue

            sensitive_values = self.X_test[sensitive_column]

            # Calculate selection rate for each group
            selection_rates = {}
            for group in sensitive_values.unique():
                group_mask = sensitive_values == group
                group_predictions = self.y_pred[group_mask]
                selection_rates[group] = np.mean(group_predictions)

            # Print selection rates
            print(f"\nSelection rates across {sensitive_column} groups:")
            for group, rate in selection_rates.items():
                print(f"{group}: {rate:.4f}")

            # Calculate max disparity
            max_rate = max(selection_rates.values())
            min_rate = min(selection_rates.values())
            selection_rate_disparity = max_rate - min_rate

            print(f"Selection rate disparity: {selection_rate_disparity:.4f}")

            # Assert demographic parity
            self.assertLessEqual(
                selection_rate_disparity,
                self.max_disparity_threshold,
                f"Selection rate disparity for {sensitive_column} exceeds threshold: {
                    selection_rate_disparity:.4f}"
            )

    def test_equalized_odds(self):
        """Test for equalized odds (equal TPR and FPR across groups)."""
        for sensitive_column in self.sensitive_features:
            # Skip if sensitive column doesn't exist
            if sensitive_column not in self.X_test.columns:
                print(
                    f"Warning: Sensitive column '{sensitive_column}' not found in dataset. Skipping.")
                continue

            sensitive_values = self.X_test[sensitive_column]

            # Calculate TPR and FPR for each group
            tpr_rates = {}
            fpr_rates = {}

            for group in sensitive_values.unique():
                group_mask = sensitive_values == group
                group_y_true = self.y_test[group_mask]
                group_y_pred = self.y_pred[group_mask]

                # True positive rate (sensitivity)
                tpr = true_positive_rate(group_y_true, group_y_pred)
                tpr_rates[group] = tpr

                # False positive rate (1 - specificity)
                fpr = false_positive_rate(group_y_true, group_y_pred)
                fpr_rates[group] = fpr

            # Print rates
            print(f"\nTrue Positive Rates across {sensitive_column} groups:")
            for group, rate in tpr_rates.items():
                print(f"{group}: {rate:.4f}")

            print(f"\nFalse Positive Rates across {sensitive_column} groups:")
            for group, rate in fpr_rates.items():
                print(f"{group}: {rate:.4f}")

            # Calculate disparities
            tpr_disparity = max(tpr_rates.values()) - min(tpr_rates.values())
            fpr_disparity = max(fpr_rates.values()) - min(fpr_rates.values())

            print(f"TPR disparity: {tpr_disparity:.4f}")
            print(f"FPR disparity: {fpr_disparity:.4f}")

            # Assert equalized odds
            self.assertLessEqual(
                tpr_disparity,
                self.max_disparity_threshold,
                f"True positive rate disparity for {sensitive_column} exceeds threshold: {
                    tpr_disparity:.4f}"
            )

            self.assertLessEqual(
                fpr_disparity,
                self.max_disparity_threshold,
                f"False positive rate disparity for {sensitive_column} exceeds threshold: {
                    fpr_disparity:.4f}"
            )


if __name__ == "__main__":
    unittest.main()
