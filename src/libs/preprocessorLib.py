import warnings

import mlflow
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.pipeline import Pipeline

from src.libs.libs import *
from src import constants

class FraudDetectionConfig:
    """Configuration class for Fraud Detection preprocessing parameters"""
    def __init__(
        self,
        ds_url,
        output_filename,
        context,
        name,
        mlflow_tracking_uri=constants.ML_FLOW_URI,
        experiment_name=constants.EXPERIMENT_NAME
    ):
        self.ds_url = ds_url
        self.output_filename = output_filename
        self.context = context
        self.name = name
        self.mlflow_tracking_uri = mlflow_tracking_uri
        self.experiment_name = experiment_name
        
        # Constants
        self.target_column = 'is_fraud'
        self.city_pop_bins = [0, 10000, 50000, 100000, 500000, 1000000, np.inf]
        self.city_pop_labels = ['<10K', '10K-50K', '50K-100K', '100K-500K', '500K-1M', '>1M']
        self.transaction_hour_bins = [-1, 5, 11, 17, 21, 24]
        self.transaction_hour_labels = ['Late Night', 'Morning', 'Afternoon', 'Evening', 'Night']
        self.drop_columns = [
            'Unnamed: 0', 'trans_date_trans_time', 'cc_num', 'merchant', 'amt',
            'first', 'last', 'street', 'city', 'state', 'zip', 'lat', 'long',
            'city_pop', 'job', 'dob', 'trans_num', 'unix_time', 'merch_lat', 'merch_long'
        ]
        self.categorical_features = [
            'category', 'gender', 'day_of_week', 'part_of_day', 'city_pop_bin'
        ]

def load_and_split_data(config):
    """
    Loads the datasets and splits them into features and target variables.
    
    Args:
        config (FraudDetectionConfig): Configuration object
        
    Returns:
        tuple: (X, y) containing features and target values
    """
    dataframe = pd.read_csv(config.ds_url)
    X_raw = dataframe.drop(columns=config.target_column, axis=1)
    y = dataframe[config.target_column]
    return X_raw, y, dataframe

def create_preprocessing_pipeline(config):
    """
    Creates and returns the preprocessing pipeline with all transformation steps.
    
    Args:
        config (FraudDetectionConfig): Configuration object
        
    Returns:
        sklearn.pipeline.Pipeline: Configured preprocessing pipeline
    """
    return Pipeline([
        ('change_dtype', ChangeDataType(columns=['trans_date_trans_time', 'dob'])),
        ('datetime_features', DateTimeFeatures(
            date_column='trans_date_trans_time',
            transaction_hour_bins=config.transaction_hour_bins,
            transaction_hour_labels=config.transaction_hour_labels
        )),
        ('age_feature', AgeFeature(dob_column='dob')),
        ('calculate_distance', CalculateDistance(
            lat_col='lat',
            long_col='long',
            merch_lat_col='merch_lat',
            merch_long_col='merch_long'
        )),
        ('bin_city_pop', BinCityPopulation(
            city_pop_bins=config.city_pop_bins,
            city_pop_labels=config.city_pop_labels
        )),
        ('yeo_johnson', YeoJohnsonTransformer()),
        ('drop_columns', DropColumns(columns=config.drop_columns)),
        ('label_encoding', LabelEncoding(columns=config.categorical_features)),
        ('scale_features', ScaleFeatures()),
    ])

def log_to_mlflow(config, preprocessed, fig1, fig2, fig3):
    """
    Logs the preprocessed datasets and related artifacts to MLflow.
    
    Args:
        config (FraudDetectionConfig): Configuration object
        preprocessed (pd.DataFrame): Preprocessed dataset
        fig1, fig2, fig3: Matplotlib figures
    """
    mlflow.set_tracking_uri(uri=config.mlflow_tracking_uri)
    mlflow.set_experiment(config.experiment_name)
    
    with mlflow.start_run(run_name=config.context) as run:
        mlflow.log_artifact(config.output_filename)
        
        dataset = mlflow.data.from_pandas(
            preprocessed,
            source=config.ds_url,
            name=config.name,
            targets=config.target_column
        )
        mlflow.log_input(dataset, context=config.context)
        mlflow.log_figure(fig1, "fraud_transaction_count.png")
        mlflow.log_figure(fig2, "corelation_matrix.png")
        mlflow.log_figure(fig3, "percentage_per_category.png")

def pie_chart_fraudulent_transactions(df, style="classic", plot_size=(6, 6)):
    # Show distribution of fraudulent vs non-fraudulent
    counts = df["is_fraud"].value_counts()
    labels = ["Non-Fraudulent", "Fraudulent"]
    sizes = [counts.get(0, 0), counts.get(1, 0)]
    colors = ["skyblue", "salmon"]
    explode = (0, 0.1)  # Slightly explode the fraud slice for emphasis

    with plt.style.context(style):
        fig, ax = plt.subplots(figsize=plot_size)
        ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90,
            colors=colors,
            explode=explode,
            shadow=True
        )
        ax.set_title("Fraudulent vs Non-Fraudulent Transactions", fontsize=14)
        plt.tight_layout()

    plt.close(fig)
    return fig

def correlation_matrix(data, style="classic", plot_size=(50, 8)):
    """
    Creates a correlation matrix heatmap for numerical columns.
    
    Args:
        data (pd.DataFrame): Input dataframe
        style (str): Matplotlib style to use
        plot_size (tuple): Figure size (width, height)
        
    Returns:
        matplotlib.figure.Figure: The generated plot figure
    """
    # Select all numeric columns (both int64 and float64)
    df_numerical = data.select_dtypes(include=[np.number])

    # Create figure and axes
    with plt.style.context(style):
        fig = plt.figure(figsize=plot_size)
        ax = fig.add_subplot(111)  # Create axes for the figure
        
        # Plot correlation matrix
        sns.heatmap(df_numerical.corr(), annot=True, cmap='coolwarm', ax=ax)
        
        # Add titles and labels
        ax.set_title("Correlation Matrix for Numerical Columns")
        
        plt.tight_layout()
    
    plt.close(fig)
    return fig

def percentage(data, style='classic', plot_size=(10, 6)):
    # Calculate the percentage of each category
    a=data[data['is_fraud']==0]['category'].value_counts(normalize=True).to_frame().reset_index()
    a.columns=['category','not fraud percentage']

    b=data[data['is_fraud']==1]['category'].value_counts(normalize=True).to_frame().reset_index()
    b.columns=['category','fraud percentage']

    ab=a.merge(b,on='category')
    ab['diff']=ab['fraud percentage']-ab['not fraud percentage']

    unique_categories = ab['category'].unique()
    palette = sns.color_palette("husl", len(unique_categories))

    color_dict = dict(zip(unique_categories, palette))    
    with plt.style.context(style):
        fig, ax = plt.subplots(figsize=plot_size)
        
        sns.barplot(y='category', 
                   x='diff', 
                   data=ab.sort_values('diff', ascending=False), 
                   hue='category', 
                   legend=False,
                   ax=ax)
        
        ax.set_xlabel('Percentage Difference')
        ax.set_ylabel('Transaction Category')
        ax.set_title('Percentage Difference of Fraudulent over Non-Fraudulent Transactions by Category')
        
        plt.tight_layout()
        
        return fig

def main(config):
    """
    Main execution function that orchestrates the preprocessing workflow.
    
    Args:
        config (FraudDetectionConfig): Configuration object
    """
    # Load and split data
    X_raw, y, dataframe = load_and_split_data(config)
    
    # Create and apply preprocessing pipeline
    preprocessor = create_preprocessing_pipeline(config)
    preprocessor.fit(X_raw)
    preprocessed = preprocessor.transform(X_raw)
    
    # Add target column back to preprocessed data
    preprocessed[config.target_column] = y.values
    
    # Save preprocessed datasets
    preprocessed.to_csv(config.output_filename, index=False)
    
    # Create visualizations
    fig1 = pie_chart_fraudulent_transactions(preprocessed)
    fig2 = correlation_matrix(preprocessed)
    fig3 = percentage(dataframe)
    
    # Log to MLflow
    log_to_mlflow(config, preprocessed, fig1, fig2, fig3)

if __name__ == "__main__":
    # Configure preprocessing parameters
    config = FraudDetectionConfig(
        ds_url=constants.VALIDATION_DATASET_URL,
        output_filename="validation_preprocessed.csv",
        context="validation",
        name="Fraud Detection in Credit Card Transactions - Validation Data Set / Preprocessed"
    )
    main(config)
