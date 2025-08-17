"""
Data processor for cleaning and preparing data for analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from sklearn.preprocessing import StandardScaler, LabelEncoder
import re

class DataProcessor:
    def __init__(self):
        self.scalers = {}
        self.encoders = {}

    def clean_dataframe(self, df: pd.DataFrame, options: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Clean a DataFrame using various techniques
        """
        if options is None:
            options = {}

        df_cleaned = df.copy()

        # Remove completely empty rows and columns
        df_cleaned = df_cleaned.dropna(how='all').dropna(axis=1, how='all')

        # Handle missing values
        missing_strategy = options.get('missing_strategy', 'auto')
        df_cleaned = self._handle_missing_values(df_cleaned, missing_strategy)

        # Convert data types
        df_cleaned = self._convert_data_types(df_cleaned)

        # Remove duplicates
        if options.get('remove_duplicates', True):
            df_cleaned = df_cleaned.drop_duplicates()

        # Handle outliers
        if options.get('remove_outliers', False):
            df_cleaned = self._remove_outliers(df_cleaned)

        return df_cleaned

    def _handle_missing_values(self, df: pd.DataFrame, strategy: str = 'auto') -> pd.DataFrame:
        """Handle missing values in the DataFrame"""
        df_copy = df.copy()

        for column in df_copy.columns:
            if df_copy[column].isnull().sum() == 0:
                continue

            if strategy == 'auto':
                # Determine strategy based on data type and missing percentage
                missing_pct = df_copy[column].isnull().sum() / len(df_copy)

                if missing_pct > 0.5:
                    # Drop columns with >50% missing values
                    df_copy = df_copy.drop(columns=[column])
                    continue

                if df_copy[column].dtype in ['object', 'category']:
                    # Fill categorical with mode
                    mode_value = df_copy[column].mode()
                    if len(mode_value) > 0:
                        df_copy[column] = df_copy[column].fillna(mode_value[0])
                    else:
                        df_copy[column] = df_copy[column].fillna('Unknown')
                else:
                    # Fill numeric with median
                    df_copy[column] = df_copy[column].fillna(df_copy[column].median())

            elif strategy == 'drop':
                df_copy = df_copy.dropna(subset=[column])

            elif strategy == 'forward_fill':
                df_copy[column] = df_copy[column].fillna(method='ffill')

            elif strategy == 'backward_fill':
                df_copy[column] = df_copy[column].fillna(method='bfill')

        return df_copy

    def _convert_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Automatically detect and convert data types"""
        df_copy = df.copy()

        for column in df_copy.columns:
            # Try to convert to numeric
            if df_copy[column].dtype == 'object':
                # Check if it's a date
                if self._is_date_column(df_copy[column]):
                    try:
                        df_copy[column] = pd.to_datetime(df_copy[column], errors='coerce')
                        continue
                    except:
                        pass

                # Check if it's numeric
                try:
                    # Remove common non-numeric characters
                    cleaned_series = df_copy[column].astype(str).str.replace(r'[,$%]', '', regex=True)
                    numeric_series = pd.to_numeric(cleaned_series, errors='coerce')

                    # If most values can be converted to numeric, use it
                    if numeric_series.notna().sum() / len(numeric_series) > 0.8:
                        df_copy[column] = numeric_series
                except:
                    pass

        return df_copy

    def _is_date_column(self, series: pd.Series) -> bool:
        """Check if a series contains date-like values"""
        # Check a sample of non-null values
        sample = series.dropna().head(10)
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
        ]

        for value in sample:
            value_str = str(value)
            for pattern in date_patterns:
                if re.match(pattern, value_str):
                    return True
        return False

    def _remove_outliers(self, df: pd.DataFrame, method: str = 'iqr') -> pd.DataFrame:
        """Remove outliers from numeric columns"""
        df_copy = df.copy()
        numeric_columns = df_copy.select_dtypes(include=[np.number]).columns

        for column in numeric_columns:
            if method == 'iqr':
                Q1 = df_copy[column].quantile(0.25)
                Q3 = df_copy[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                df_copy = df_copy[(df_copy[column] >= lower_bound) & (df_copy[column] <= upper_bound)]

            elif method == 'zscore':
                z_scores = np.abs((df_copy[column] - df_copy[column].mean()) / df_copy[column].std())
                df_copy = df_copy[z_scores < 3]

        return df_copy

    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get comprehensive summary of the DataFrame"""
        summary = {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': dict(df.dtypes.astype(str)),
            'missing_values': dict(df.isnull().sum()),
            'memory_usage': df.memory_usage(deep=True).sum(),
        }

        # Numeric columns summary
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            summary['numeric_summary'] = df[numeric_cols].describe().to_dict()

        # Categorical columns summary
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            summary['categorical_summary'] = {}
            for col in categorical_cols:
                summary['categorical_summary'][col] = {
                    'unique_values': df[col].nunique(),
                    'top_values': df[col].value_counts().head(5).to_dict()
                }

        return summary

    def prepare_for_ml(self, df: pd.DataFrame, target_column: str = None) -> Dict[str, Any]:
        """Prepare DataFrame for machine learning"""
        df_ml = df.copy()

        # Encode categorical variables
        categorical_cols = df_ml.select_dtypes(include=['object', 'category']).columns

        for col in categorical_cols:
            if col != target_column:  # Don't encode target if it's categorical
                le = LabelEncoder()
                df_ml[col] = le.fit_transform(df_ml[col].astype(str))
                self.encoders[col] = le

        # Scale numeric features
        numeric_cols = df_ml.select_dtypes(include=[np.number]).columns
        if target_column and target_column in numeric_cols:
            numeric_cols = numeric_cols.drop(target_column)

        if len(numeric_cols) > 0:
            scaler = StandardScaler()
            df_ml[numeric_cols] = scaler.fit_transform(df_ml[numeric_cols])
            self.scalers['features'] = scaler

        return {
            'data': df_ml,
            'encoders': self.encoders,
            'scalers': self.scalers,
            'feature_columns': [col for col in df_ml.columns if col != target_column],
            'target_column': target_column
        }
