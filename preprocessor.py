import os
import logging
import joblib
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
from sklearn.preprocessing import StandardScaler
from typing import Tuple, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatteryDataPreprocessor:
    """
    Automated data cleaning, noise reduction, target estimation (SOH/RUL),
    and feature engineering pipeline for lithium-ion battery operational logs.
    """
    
    def __init__(self, nominal_capacity_ah: float = 2.0, eol_soh_threshold: float = 80.0):
        """
        :param nominal_capacity_ah: Rated capacity of the battery in Ampere-hours.
        :param eol_soh_threshold: State of Health percentage defining End-of-Life (EOL).
        """
        self.nominal_capacity_ah = nominal_capacity_ah
        self.eol_soh_threshold = eol_soh_threshold
        self.scaler = StandardScaler()
        self.feature_columns = [
            'cycle_number', 
            'peak_voltage_v', 
            'avg_temp_c', 
            'internal_resistance_ohm', 
            'capacity_fade_rate'
        ]

    def apply_butterworth_filter(self, data: pd.Series, cutoff: float = 0.1, fs: float = 1.0, order: int = 2) -> np.ndarray:
        """
        Applies a low-pass Butterworth filter (zero-phase forward-backward) to smooth sensor noise.
        """
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return filtfilt(b, a, data.values)

    def compute_soh_and_rul(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates State of Health (SOH) and Remaining Useful Life (RUL) target labels.
        
        SOH = (C_current / C_nominal) * 100
        RUL = Cycle_EOL - Cycle_current
        """
        df = df.sort_values(by='cycle_number').reset_index(drop=True)
        
        # Calculate State of Health (SOH)
        df['soh_percent'] = (df['capacity_ah'] / self.nominal_capacity_ah) * 100.0
        
        # Determine EOL Cycle index (first cycle where SOH falls below threshold)
        eol_idx = df[df['soh_percent'] <= self.eol_soh_threshold].index.min()
        
        if pd.isna(eol_idx):
            # If threshold is not crossed in dataset, set max cycle as reference EOL
            total_eol_cycle = df['cycle_number'].max()
        else:
            total_eol_cycle = df.loc[eol_idx, 'cycle_number']
            
        # Target Variable RUL: Remaining cycles until EOL
        df['rul_cycles'] = total_eol_cycle - df['cycle_number']
        
        # Clip negative RUL values for cycles post-EOL
        df['rul_cycles'] = df['rul_cycles'].clip(lower=0)
        
        return df

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generates physical degradation metrics and moving-window trends.
        """
        # Smooth capacity readings using Butterworth filter
        df['capacity_filtered'] = self.apply_butterworth_filter(df['capacity_ah'])
        
        # Calculate Capacity Fade Rate: delta_capacity / delta_cycle
        df['capacity_fade_rate'] = df['capacity_filtered'].diff().fillna(0.0) / df['cycle_number'].diff().fillna(1.0)
        
        # Handle initial state edge cases
        df['capacity_fade_rate'] = df['capacity_fade_rate'].abs()
        
        return df

    def fit_transform(self, raw_df: pd.DataFrame, artifact_save_dir: str = "models/artifacts") -> Tuple[np.ndarray, np.ndarray, pd.DataFrame]:
        """
        Executes full preprocessing pipeline and saves the standardizer artifact.
        """
        logger.info("Executing ingestion, cleaning, and feature engineering...")
        
        processed_df = self.compute_soh_and_rul(raw_df)
        processed_df = self.engineer_features(processed_df)
        
        X = processed_df[self.feature_columns].values
        y = processed_df['rul_cycles'].values
        
        X_scaled = self.scaler.fit_transform(X)
        
        os.makedirs(artifact_save_dir, exist_ok=True)
        scaler_path = os.path.join(artifact_save_dir, "scaler.pkl")
        joblib.dump(self.scaler, scaler_path)
        logger.info(f"Feature scaler saved successfully at {scaler_path}")
        
        return X_scaled, y, processed_df

    def transform_single_instance(self, input_features: Dict[str, Any], scaler_path: str = "models/artifacts/scaler.pkl") -> np.ndarray:
        """
        Transforms a single live inference input dictionary using saved scaler artifacts.
        """
        scaler = joblib.load(scaler_path)
        feature_vector = np.array([[
            input_features['cycle_number'],
            input_features['peak_voltage_v'],
            input_features['avg_temp_c'],
            input_features['internal_resistance_ohm'],
            input_features['capacity_fade_rate']
        ]])
        return scaler.transform(feature_vector)