import os
import pytest
import numpy as np
import pandas as pd
from models.preprocessor import BatteryDataPreprocessor
from models.trainer import RULModelTrainer

@pytest.fixture
def mock_cycle_data():
    cycles = np.arange(1, 101)
    return pd.DataFrame({
        'battery_id': ['TEST_BAT_01'] * 100,
        'cycle_number': cycles,
        'capacity_ah': 2.0 - (0.003 * cycles),
        'peak_voltage_v': 4.2 - (0.002 * cycles),
        'avg_temp_c': 25.0 + (0.05 * cycles),
        'internal_resistance_ohm': 0.015 + (0.0001 * cycles)
    })

def test_soh_rul_computation(mock_cycle_data):
    preprocessor = BatteryDataPreprocessor(nominal_capacity_ah=2.0, eol_soh_threshold=80.0)
    df = preprocessor.compute_soh_and_rul(mock_cycle_data)
    
    # Verify maximum initial SOH is 100%
    assert df.loc[0, 'soh_percent'] == 100.0
    # Verify RUL decreases as cycle count grows
    assert df.loc[0, 'rul_cycles'] > df.loc[50, 'rul_cycles']
    # Verify non-negative RUL bounds
    assert (df['rul_cycles'] >= 0).all()

def test_mlp_trainer_pipeline(mock_cycle_data):
    preprocessor = BatteryDataPreprocessor(nominal_capacity_ah=2.0)
    X_scaled, y, _ = preprocessor.fit_transform(mock_cycle_data, artifact_save_dir="tests/artifacts")
    
    trainer = RULModelTrainer()
    summary_df = trainer.train_and_benchmark(X_scaled, y, artifact_dir="tests/artifacts")
    
    assert not summary_df.empty
    assert "MLPRegressor" in summary_df["Model Architecture"].values
    
    # R2 score must exceed threshold on clean degradation profiles
    mlp_r2 = summary_df.loc[summary_df["Model Architecture"] == "MLPRegressor", "R² Score"].values[0]
    assert mlp_r2 > 0.90