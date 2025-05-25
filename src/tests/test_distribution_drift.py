import unittest

import pandas as pd
from scipy.stats import ks_2samp
from sklearn.model_selection import train_test_split

from src.constants import TARGET_COLUMN
from src.libs.libs import SMOTESampler

# Data Distribution Checks
# Train vs. Test Distribution Drift
# This test compares two continuous distributions to determine whether
# they are significantly different.


class TestDistributionDrift(unittest.TestCase):
    """Test class to check for distribution drift between train and test sets."""

    @classmethod
    def setUpClass(cls):
        """Set up test data once for all test methods."""
        # Load into DataFrame
        cls.train_preprocessed = pd.read_csv("train_preprocessed.csv")

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

        cls.columns = cls.X_train.columns.tolist()

    def ks_test(self, feature):
        """Perform KS test for the specified feature.

        Args:
            feature: The column name to test

        Returns:
            tuple: (ks_statistic, p_value)
        """
        train_feature = self.X_train[feature]
        test_feature = self.X_test[feature]

        # Perform the KS test
        ks_stat, p_value = ks_2samp(train_feature, test_feature)
        return ks_stat, p_value

    def test_all_features_distribution(self):
        """Test that all features have similar distributions in train and test sets."""
        # Set significance level - standard alpha and special alpha for distance
        standard_alpha = 0.05
        distance_alpha = 0.01

        # Store failed features for reporting
        failed_features = []
        skipped_features = []

        print("\nKS Test Results for All Columns:")
        print("-" * 80)
        print(
            f"{'Column Name':<30} {'KS-statistic':<15} {'p-value':<15} {'Alpha':<10} {'Result':<10}"
        )
        print("-" * 80)

        for column_name in self.columns:
            try:
                # Use different alpha for distance feature
                alpha = distance_alpha if column_name == "distance" else standard_alpha

                ks_stat, p_value = self.ks_test(column_name)
                result = "PASS" if p_value > alpha else "FAIL"
                print(
                    f"{column_name:<30} "
                    f"{ks_stat:<15.6f} "
                    f"{p_value:<15.6f} "
                    f"{alpha:<10.3f} "
                    f"{result:<10}"
                )

                if p_value <= alpha:
                    failed_features.append((column_name, ks_stat, p_value, alpha))
            except Exception as e:
                print(f"{column_name:<30} Error: {str(e)}")
                skipped_features.append((column_name, str(e)))

        print("-" * 80)

        # Assert that no features have distribution drift
        if failed_features:
            failure_message = (
                "\nDistribution drift detected in the following features:\n"
            )
            for feature, ks_stat, p_value, alpha in failed_features:
                failure_message += f"  - {feature}: KS-statistic={ks_stat:.6f}, "
                f"p-value={p_value:.6f}, "
                f"alpha={alpha:.3f}\n"

            if skipped_features:
                failure_message += "\nSkipped features due to errors:\n"
                for feature, error in skipped_features:
                    failure_message += f"  - {feature}: {error}\n"

            self.fail(failure_message)

    def test_individual_features(self):
        """Generate individual test methods for each feature."""
        # Set significance levels
        standard_alpha = 0.05
        distance_alpha = 0.01

        for column_name in self.columns:
            # Create a test method name based on the column name
            test_name = f"test_feature_{
                column_name.replace(
                    ' ', '_').replace(
                    '-', '_')}"

            # Define the test method with appropriate alpha based on column name
            def test_method(self, column=column_name):
                try:
                    # Use different alpha for distance feature
                    alpha = distance_alpha if column == "distance" else standard_alpha

                    ks_stat, p_value = self.ks_test(column)
                    self.assertGreater(
                        p_value,
                        alpha,
                        f"Distribution drift detected in feature '{column}': "
                        f"KS-statistic={ks_stat:.6f}, p-value={p_value:.6f}, alpha={alpha:.3f}",
                    )
                except Exception as e:
                    self.fail(f"Error testing feature '{column}': {str(e)}")

            # Add the test method to the class
            setattr(TestDistributionDrift, test_name, test_method)


if __name__ == "__main__":
    unittest.main()
