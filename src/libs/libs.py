import numpy as np
import pandas as pd
from imblearn.combine import SMOTETomek
from imblearn.over_sampling import ADASYN, SMOTE
from imblearn.under_sampling import TomekLinks
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix)
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, PowerTransformer


class ChangeDataType(BaseEstimator, TransformerMixin):
    # Converts specified columns to datetime format.
    def __init__(self, columns):
        self.columns = columns

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        for col in self.columns:
            X[col] = pd.to_datetime(X[col], errors="coerce")
        return X


class DateTimeFeatures(BaseEstimator, TransformerMixin):
    # Extracts date and time-related features like hour, month, day of the
    # week, and part of the day.
    def __init__(self, date_column, transaction_hour_bins, transaction_hour_labels):
        self.date_column = date_column
        self.transaction_hour_bins = transaction_hour_bins
        self.transaction_hour_labels = transaction_hour_labels
        self.new_columns = [
            "transaction_hour",
            "transaction_month",
            "is_weekend",
            "day_of_week",
            "part_of_day",
        ]

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        X["transaction_hour"] = X[self.date_column].dt.hour
        X["transaction_month"] = X[self.date_column].dt.month
        X["is_weekend"] = (
            X[self.date_column].dt.weekday.isin([5, 6]).round().astype("int64")
        )

        # Day of week: Monday=0, Sunday=6
        X["day_of_week"] = X[self.date_column].dt.day_name()

        # Part of day classification
        X["part_of_day"] = pd.cut(
            X["transaction_hour"],
            bins=self.transaction_hour_bins,
            labels=self.transaction_hour_labels,
            right=True,
        )
        return X


class AgeFeature(BaseEstimator, TransformerMixin):
    # Calculates age based on the date of birth (DOB) column.
    def __init__(self, dob_column):
        self.dob_column = dob_column
        self.new_column = "age"

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        reference_date = pd.Timestamp(2020, 12, 31)
        X[self.new_column] = (reference_date - X[self.dob_column]).dt.days // 365
        return X


class CalculateDistance(BaseEstimator, TransformerMixin):
    # Calculates the distance between two geographical points using the
    # Haversine formula.
    def __init__(self, lat_col, long_col, merch_lat_col, merch_long_col):
        self.lat_col = lat_col
        self.long_col = long_col
        self.merch_lat_col = merch_lat_col
        self.merch_long_col = merch_long_col
        self.new_column = "distance"

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()

        # Convert latitudes and longitudes to radians
        lat1 = np.radians(X[self.lat_col])
        lon1 = np.radians(X[self.long_col])
        lat2 = np.radians(X[self.merch_lat_col])
        lon2 = np.radians(X[self.merch_long_col])

        # Haversine formula to calculate distance
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        R = 6371  # Radius of the Earth in kilometers
        X[self.new_column] = R * c  # Distance in kilometers

        return X


class BinCityPopulation(BaseEstimator, TransformerMixin):
    # Groups city population into bins with specified labels.
    def __init__(self, city_pop_bins, city_pop_labels):
        self.city_pop_bins = city_pop_bins
        self.city_pop_labels = city_pop_labels
        self.new_column = "city_pop_bin"

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        X[self.new_column] = pd.cut(
            X["city_pop"], bins=self.city_pop_bins, labels=self.city_pop_labels
        )
        return X


class YeoJohnsonTransformer(BaseEstimator, TransformerMixin):
    # Applies the Yeo-Johnson transformation to normalize the 'amt' column.
    def __init__(self):
        self.transformer = PowerTransformer(method="yeo-johnson")
        self.new_column = "amt_yeo_johnson"

    def fit(self, X, y=None):
        self.transformer.fit(X[["amt"]])
        return self

    def transform(self, X):
        X = X.copy()
        X[self.new_column] = self.transformer.transform(X[["amt"]])
        return X


class DropColumns(BaseEstimator, TransformerMixin):
    # Drops specified columns from the dataset.
    def __init__(self, columns):
        self.columns = columns

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.drop(columns=self.columns, errors="ignore")
        self.remaining_columns = X.columns
        return X


class LabelEncoding(BaseEstimator, TransformerMixin):
    # Performs label encoding for specified categorical columns.
    def __init__(self, columns):
        self.columns = columns
        self.label_encoders = {}

    def fit(self, X, y=None):
        for col in self.columns:
            le = LabelEncoder()
            le.fit(X[col])
            self.label_encoders[col] = le
        return self

    def transform(self, X):
        X = X.copy()
        for col in self.columns:
            X[col] = self.label_encoders[col].transform(X[col])
        return X


class ScaleFeatures(BaseEstimator, TransformerMixin):
    # Scales numerical features to a range of 0 to 1 using MinMaxScaler.
    def __init__(self):
        self.scaler = MinMaxScaler()

    def fit(self, X, y=None):
        self.scaler.fit(X)
        return self

    def transform(self, X):
        X = X.copy()
        X[:] = self.scaler.transform(X)
        return X

    # Preprocessing pipeline


# Class to oversample the minority class using the Synthetic Minority
# Over-sampling Technique (SMOTE)


class SMOTESampler:
    def __init__(self, target_column):
        self.target_column = target_column
        self.sampler = SMOTE(random_state=random_state)

    # Fits the sampler and resamples the data to balance the target column
    def fit_resample(self, df):
        X = df.drop(columns=[self.target_column])
        y = df[self.target_column]
        X_resampled, y_resampled = self.sampler.fit_resample(X, y)
        return X_resampled.assign(**{self.target_column: y_resampled})


# Class to oversample the minority class using the Adaptive Synthetic (ADASYN) method
class ADASYN_Sampler:
    def __init__(self, target_column):
        self.target_column = target_column
        self.sampler = ADASYN(random_state=random_state)

    # Fits the sampler and resamples the data to balance the target column
    def fit_resample(self, df):
        X = df.drop(columns=[self.target_column])
        y = df[self.target_column]
        X_resampled, y_resampled = self.sampler.fit_resample(X, y)
        return X_resampled.assign(**{self.target_column: y_resampled})


# Class to reduce data imbalance by removing Tomek Links (overlapping
# majority samples near minority samples)
class TomekLinksSampler:
    def __init__(self, target_column):
        self.target_column = target_column
        self.sampler = TomekLinks()

    # Fits the sampler and resamples the data to reduce Tomek Links
    def fit_resample(self, df):
        X = df.drop(columns=[self.target_column])
        y = df[self.target_column]
        X_resampled, y_resampled = self.sampler.fit_resample(X, y)
        return X_resampled.assign(**{self.target_column: y_resampled})


# Class to combine SMOTE oversampling and Tomek Links removal for handling
# imbalanced data
class SMOTETomekSampler:
    def __init__(self, target_column):
        self.target_column = target_column
        self.sampler = SMOTETomek(random_state=random_state)

    # Fits the sampler and resamples the data using a combination of SMOTE and
    # Tomek Links
    def fit_resample(self, df):
        X = df.drop(columns=[self.target_column])
        y = df[self.target_column]
        X_resampled, y_resampled = self.sampler.fit_resample(X, y)
        return X_resampled.assign(**{self.target_column: y_resampled})


random_state = 15

# 1. Logistic Regression


def print_score(clf, X_train, y_train, X_test, y_test, train=True):
    if train:
        pred = clf.predict(X_train)
        clf_report = pd.DataFrame(
            classification_report(y_train, pred, output_dict=True)
        )
        print("Train Result:\n================================================")
        print(f"Accuracy Score: {accuracy_score(y_train, pred) * 100:.2f}%")
        print("_______________________________________________")
        print(f"CLASSIFICATION REPORT:\n{clf_report}")
        print("_______________________________________________")
        print(f"Confusion Matrix: \n {confusion_matrix(y_train, pred)}\n")

    elif not train:
        pred = clf.predict(X_test)
        clf_report = pd.DataFrame(classification_report(y_test, pred, output_dict=True))
        print("Test Result:\n================================================")
        print(f"Accuracy Score: {accuracy_score(y_test, pred) * 100:.2f}%")
        print("_______________________________________________")
        print(f"CLASSIFICATION REPORT:\n{clf_report}")
        print("_______________________________________________")
        print(f"Confusion Matrix: \n {confusion_matrix(y_test, pred)}\n")
