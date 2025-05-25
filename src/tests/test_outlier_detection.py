import unittest
import numpy as np
import pandas as pd
from scipy.stats import zscore
from src.libs.libs import SMOTESampler
from sklearn.model_selection import train_test_split
from src.constants import TARGET_COLUMN


class TestOutlierDetection(unittest.TestCase):
    """Test class to check for outliers in the dataset using Z-scores."""

    @classmethod
    def setUpClass(cls):
        """Set up test data once for all test methods."""
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

        # Get all column names
        cls.columns = cls.X_train.columns.tolist()

    def detect_outliers_zscore(self, feature, threshold=3.0):
        """Detect outliers in a feature using Z-score method.

        Args:
            feature: The column name to check for outliers
            threshold: Z-score threshold for outlier detection (default: 3.0)

        Returns:
            tuple: (outlier_count, outlier_percentage, max_zscore)
        """
        # Get feature data
        feature_data = self.X_train[feature]

        # Skip non-numeric features
        if not np.issubdtype(feature_data.dtype, np.number):
            return 0, 0.0, 0.0

        # Calculate Z-scores
        try:
            z_scores = np.abs(zscore(feature_data, nan_policy='omit'))

            # Count outliers
            outliers = np.sum(z_scores > threshold)
            outlier_percentage = (outliers / len(feature_data)) * 100
            max_zscore = np.max(z_scores) if len(z_scores) > 0 else 0

            return outliers, outlier_percentage, max_zscore
        except Exception:
            # Handle features that can't be processed (e.g., constant values)
            return 0, 0.0, 0.0

    def test_outliers_in_all_features(self):
        """Test for outliers in all features of the dataset."""
        # Set threshold for outlier detection
        threshold = 3.0

        # Set threshold for acceptable percentage of outliers
        max_acceptable_percentage = 5.0

        # Store features with excessive outliers
        problematic_features = []
        skipped_features = []

        print("\nOutlier Detection Results (Z-score method):")
        print("-" * 80)
        print(f"{'Feature Name':<30} {'Outliers':<10} {'Percentage':<12} {'Max Z-score':<12} {'Status':<10}")
        print("-" * 80)

        for feature in self.columns:
            try:
                outliers, percentage, max_zscore = self.detect_outliers_zscore(feature, threshold)

                # Determine status
                if not np.issubdtype(self.X_train[feature].dtype, np.number):
                    status = "SKIPPED"
                    skipped_features.append((feature, "Non-numeric"))
                elif percentage > max_acceptable_percentage:
                    status = "WARNING"
                    problematic_features.append((feature, outliers, percentage, max_zscore))
                else:
                    status = "OK"

                print(f"{feature:<30} {outliers:<10} {percentage:<12.2f}% {max_zscore:<12.2f} {status:<10}")

            except Exception as e:
                print(f"{feature:<30} Error: {str(e)}")
                skipped_features.append((feature, str(e)))

        print("-" * 80)

        # Report features with excessive outliers
        if problematic_features:
            warning_message = "\nFeatures with excessive outliers (>5%):\n"
            for feature, count, percentage, max_zscore in problematic_features:
                warning_message += f"  - {feature}: {count} outliers ({percentage:.2f}%), max Z-score: {max_zscore:.2f}\n"

            print(warning_message)
            print("Consider handling these outliers using clipping, transformation, or removal.")

        if skipped_features:
            print("\nSkipped features:")
            for feature, reason in skipped_features:
                print(f"  - {feature}: {reason}")

    def test_individual_features_for_outliers(self):
        """Generate individual test methods for each numeric feature."""
        # Set threshold for outlier detection
        threshold = 3.0

        # Set threshold for acceptable percentage of outliers
        max_acceptable_percentage = 5.0

        for feature in self.columns:
            # Skip non-numeric features
            if not np.issubdtype(self.X_train[feature].dtype, np.number):
                continue

            # Create a test method name based on the feature name
            test_name = f"test_outliers_in_{feature.replace(' ', '_').replace('-', '_')}"

            # Define the test method
            def test_method(self, feature=feature):
                try:
                    outliers, percentage, max_zscore = self.detect_outliers_zscore(feature, threshold)

                    # Assert that the percentage of outliers is within acceptable limits
                    self.assertLessEqual(
                        percentage, max_acceptable_percentage,
                        f"Excessive outliers detected in feature '{feature}': "
                        f"{outliers} outliers ({percentage:.2f}%), max Z-score: {max_zscore:.2f}"
                    )
                except Exception as e:
                    self.fail(f"Error testing feature '{feature}': {str(e)}")

            # Add the test method to the class
            setattr(TestOutlierDetection, test_name, test_method)


if __name__ == "__main__":
    unittest.main()