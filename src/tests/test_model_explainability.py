import unittest
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.inspection import permutation_importance
import mlflow
import mlflow.sklearn
import matplotlib.pyplot as plt
from src.libs.libs import SMOTESampler
from src.constants import TARGET_COLUMN, MODEL_URI


class TestModelExplainability(unittest.TestCase):
    """Test class to evaluate model explainability using permutation importance."""

    @classmethod
    def setUpClass(cls):
        """Set up test data and model once for all test methods."""
        # Define model URI
        cls.MODEL_URI = MODEL_URI

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

        # Load the model
        cls.model = mlflow.sklearn.load_model(cls.MODEL_URI)

        # Create output directory for results if it doesn't exist
        os.makedirs("output", exist_ok=True)

    def test_model_has_feature_importances(self):
        """Test that the model has built-in feature importances."""
        # Check if model has feature_importances_ attribute (common in tree-based
        # models)
        self.assertTrue(
            hasattr(self.model, "feature_importances_"),
            "Model should have built-in feature importances",
        )

        # Check that feature importances are valid
        importances = self.model.feature_importances_
        self.assertEqual(
            len(importances),
            len(self.X_train.columns),
            "Number of feature importances should match number of features",
        )
        self.assertAlmostEqual(
            sum(importances),
            1.0,
            msg="Sum of feature importances should be approximately 1.0",
            places=5,
        )

    def test_permutation_importance(self):
        """Test permutation importance calculation and validate results."""
        # Calculate permutation importance
        result = permutation_importance(
            self.model, self.X_test, self.y_test, n_repeats=10, random_state=42
        )

        # Format results
        perm_importance_df = pd.DataFrame(
            {
                "Feature": self.X_test.columns,
                "Importance": result.importances_mean,
                "Std": result.importances_std,
            }
        ).sort_values(by="Importance", ascending=False)

        # Print the top 10 features by permutation importance
        print("\nTop 10 Features by Permutation Importance:")
        print(perm_importance_df.head(10).to_string())

        # Save results to CSV
        output_file = "output/permutation_importance_results.csv"
        perm_importance_df.to_csv(output_file, index=False)
        print(f"\nFull permutation importance results saved to {output_file}")

        # Test 1: Check that permutation importance results exist
        self.assertIsNotNone(result, "Permutation importance result should not be None")
        self.assertGreater(
            len(result.importances_mean),
            0,
            "Permutation importance should have results",
        )

        # Test 2: Check that at least some features have non-zero importance
        self.assertGreater(
            np.sum(result.importances_mean > 0),
            0,
            "At least some features should have positive importance",
        )

        # Test 3: Check that top features have significant importance
        top_importance = perm_importance_df["Importance"].iloc[0]
        self.assertGreater(
            top_importance,
            0.01,
            f"Top feature should have meaningful importance, got {top_importance}",
        )

        # Test 4: Generate and save permutation importance plot
        plt.figure(figsize=(10, 8))
        features = perm_importance_df["Feature"].head(15)
        importances = perm_importance_df["Importance"].head(15)
        std = perm_importance_df["Std"].head(15)

        plt.barh(features, importances)
        plt.xlabel("Permutation Importance")
        plt.title("Top 15 Features by Permutation Importance")

        # Save plot
        plot_path = "output/permutation_importance_plot.png"
        plt.tight_layout()
        plt.savefig(plot_path)
        plt.close()

        # Check that plot was created
        self.assertTrue(
            os.path.exists(plot_path), f"Plot file {plot_path} should exist"
        )
        print(f"Permutation importance plot saved to {plot_path}")

    def test_compare_feature_importance_methods(self):
        """Test comparison between built-in and permutation importance."""
        # Calculate permutation importance
        result = permutation_importance(
            self.model, self.X_test, self.y_test, n_repeats=5, random_state=42
        )

        # Get built-in feature importances
        built_in_importances = pd.DataFrame(
            {
                "Feature": self.X_test.columns,
                "Built_in_Importance": self.model.feature_importances_,
            }
        )

        # Get permutation importances
        perm_importances = pd.DataFrame(
            {
                "Feature": self.X_test.columns,
                "Permutation_Importance": result.importances_mean,
            }
        )

        # Merge the two
        comparison_df = pd.merge(built_in_importances, perm_importances, on="Feature")
        comparison_df = comparison_df.sort_values(
            by="Built_in_Importance", ascending=False
        )

        # Print comparison of top 10 features
        print("\nComparison of Feature Importance Methods (Top 10):")
        print(comparison_df.head(10).to_string())

        # Save comparison to CSV
        output_file = "output/feature_importance_comparison.csv"
        comparison_df.to_csv(output_file, index=False)
        print(f"\nFeature importance comparison saved to {output_file}")

        # Test: Check for some correlation between the two methods
        correlation = comparison_df["Built_in_Importance"].corr(
            comparison_df["Permutation_Importance"]
        )
        print(
            f"\nCorrelation between built-in and permutation importance: {correlation:.4f}"
        )

        # The correlation doesn't need to be perfect, but should show some relationship
        # A very low or negative correlation might indicate issues with the model
        self.assertGreater(
            correlation,
            0.1,
            f"Built-in and permutation importance should show some correlation, got {correlation:.4f}",
        )

        # Create scatter plot to visualize relationship
        plt.figure(figsize=(8, 8))
        plt.scatter(
            comparison_df["Built_in_Importance"],
            comparison_df["Permutation_Importance"],
            alpha=0.7,
        )
        plt.xlabel("Built-in Feature Importance")
        plt.ylabel("Permutation Importance")
        plt.title("Comparison of Feature Importance Methods")

        # Add feature names for top features
        for i, row in comparison_df.head(5).iterrows():
            plt.annotate(
                row["Feature"],
                (row["Built_in_Importance"], row["Permutation_Importance"]),
                xytext=(5, 5),
                textcoords="offset points",
            )

        # Add diagonal line for reference
        max_val = max(
            comparison_df["Built_in_Importance"].max(),
            comparison_df["Permutation_Importance"].max(),
        )
        plt.plot([0, max_val], [0, max_val], "k--", alpha=0.5)

        # Save plot
        plot_path = "output/importance_comparison_plot.png"
        plt.tight_layout()
        plt.savefig(plot_path)
        plt.close()

        # Check that plot was created
        self.assertTrue(
            os.path.exists(plot_path), f"Plot file {plot_path} should exist"
        )
        print(f"Importance comparison plot saved to {plot_path}")


if __name__ == "__main__":
    unittest.main()
