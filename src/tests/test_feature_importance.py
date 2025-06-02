import os
import unittest

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split

import sys
import pickle

# Add the project root to the path to ensure correct imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.constants import TARGET_COLUMN, TRAIN_DATASET_FILE_NAME, LOCAL_MODEL_PATH
from src.libs.libs import SMOTESampler


class TestFeatureImportance(unittest.TestCase):
    """Test class to analyze and validate feature importance."""

    def load_model():
        model_uri = LOCAL_MODEL_PATH
        with open(model_uri, "rb") as f:
            model = pickle.load(f)
        return model

    @classmethod
    def setUpClass(cls):
        """Set up test data and model once for all test methods."""
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

        cls.model = cls.load_model()

        # Get built-in feature importances
        cls.importances = cls.model.feature_importances_

        # Create DataFrame
        cls.feature_importance_df = pd.DataFrame(
            {"Feature": cls.X_train.columns, "Importance": cls.importances}
        ).sort_values(by="Importance", ascending=False)

        # Create output directory for plots if it doesn't exist
        os.makedirs("output", exist_ok=True)

    def test_feature_importance_exists(self):
        """Test that feature importances exist and are valid."""
        self.assertIsNotNone(self.importances, "Feature importances should not be None")
        self.assertEqual(
            len(self.importances),
            len(self.X_train.columns),
            "Number of feature importances should match number of features",
        )
        self.assertGreater(
            sum(self.importances), 0, "Sum of feature importances should be positive"
        )
        self.assertAlmostEqual(
            sum(self.importances),
            1.0,
            places=5,
            msg="Sum of feature importances should be approximately 1.0",
        )

    def test_top_features_have_significant_importance(self):
        """Test that top features have significant importance."""
        # Get top 5 features
        top_features = self.feature_importance_df.head(5)

        # Assert that top features have significant importance (e.g., at least 3%)
        for _, row in top_features.iterrows():
            self.assertGreaterEqual(
                row["Importance"],
                0.03,
                f"Top feature '{row['Feature']}' should have importance of at least 5%",
            )

        # Assert that top 5 features collectively account for significant portion
        # of importance
        top_importance_sum = top_features["Importance"].sum()
        self.assertGreaterEqual(
            top_importance_sum,
            0.5,
            f"Top 5 features should account for at least 50% of total importance, "
            f"got {top_importance_sum:.2f}",
        )

    def test_generate_feature_importance_plot(self):
        """Generate feature importance plot and save to file."""
        # Create plot
        plt.figure(figsize=(10, 6))
        plt.barh(
            self.feature_importance_df["Feature"],
            self.feature_importance_df["Importance"],
        )
        plt.xlabel("Importance")
        plt.title("Built-in Feature Importance")
        plt.gca().invert_yaxis()

        # Save plot to file instead of showing it
        plot_path = "output/feature_importance.png"
        plt.savefig(plot_path)
        plt.close()

        # Assert that the plot file was created
        self.assertTrue(
            os.path.exists(plot_path), f"Plot file {plot_path} should exist"
        )
        self.assertGreater(
            os.path.getsize(plot_path), 0, f"Plot file {plot_path} should not be empty"
        )

        print(f"Feature importance plot saved to {plot_path}")

        # Print top 10 features for reference
        print("\nTop 10 Most Important Features:")
        for i, (_, row) in enumerate(self.feature_importance_df.head(10).iterrows(), 1):
            print(f"{i}. {row['Feature']}: {row['Importance']:.4f}")


if __name__ == "__main__":
    unittest.main()
