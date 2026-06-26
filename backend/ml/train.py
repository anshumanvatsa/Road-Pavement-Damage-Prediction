"""Train ML model for road degradation prediction."""
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb


# Feature columns - must match predict.py
FEATURE_COLUMNS = [
    "traffic_volume",
    "heavy_vehicle_percentage",
    "rainfall",
    "temperature",
    "humidity",
    "condition",
]
TARGET_COLUMN = "degradation"


def generate_synthetic_data(n_samples: int = 5000) -> pd.DataFrame:
    """Generate synthetic training data matching digital-twin degradation logic."""
    np.random.seed(42)

    traffic_volume = np.random.uniform(1000, 20000, n_samples)
    heavy_vehicle_percentage = np.random.uniform(0, 40, n_samples)
    rainfall = np.random.uniform(0, 300, n_samples)
    temperature = np.random.uniform(5, 45, n_samples)
    humidity = np.random.uniform(20, 90, n_samples)
    condition = np.random.uniform(30, 100, n_samples)

    # Degradation formula from digital-twin.ts
    traffic_factor = (traffic_volume / 10000) * 2
    heavy_factor = (heavy_vehicle_percentage / 100) * 5
    rainfall_factor = (rainfall / 300) * 3
    temp_factor = np.abs(temperature - 20) / 20 * 2
    humidity_factor = (humidity / 100) * 1.5

    base_degradation = (
        traffic_factor + heavy_factor + rainfall_factor + temp_factor + humidity_factor
    )
    condition_multiplier = 1 + (100 - condition) / 100
    degradation = base_degradation * condition_multiplier

    # Add noise
    noise = np.random.normal(0, 0.5, n_samples)
    degradation = np.clip(degradation + noise, 0.1, 50)

    return pd.DataFrame(
        {
            "traffic_volume": traffic_volume,
            "heavy_vehicle_percentage": heavy_vehicle_percentage,
            "rainfall": rainfall,
            "temperature": temperature,
            "humidity": humidity,
            "condition": condition,
            "degradation": degradation,
        }
    )


def train_models(X: pd.DataFrame, y: pd.Series) -> tuple:
    """Train both XGBoost and RandomForest, return the best performer."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # XGBoost
    xgb_model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
    )
    xgb_model.fit(X_train, y_train)
    xgb_pred = xgb_model.predict(X_test)
    xgb_mae = mean_absolute_error(y_test, xgb_pred)
    xgb_r2 = r2_score(y_test, xgb_pred)

    # RandomForest
    rf_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
    )
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)
    rf_mae = mean_absolute_error(y_test, rf_pred)
    rf_r2 = r2_score(y_test, rf_pred)

    # Use XGBoost if better, else RandomForest
    if xgb_r2 >= rf_r2:
        return xgb_model, "xgboost", {"mae": xgb_mae, "r2": xgb_r2}
    return rf_model, "random_forest", {"mae": rf_mae, "r2": rf_r2}


def main():
    """Train and save the model."""
    print("Generating synthetic training data...")
    df = generate_synthetic_data(5000)

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    print("Training models (XGBoost + RandomForest)...")
    model, model_type, metrics = train_models(X, y)

    print(f"Selected model: {model_type}")
    print(f"  MAE: {metrics['mae']:.4f}")
    print(f"  R²:  {metrics['r2']:.4f}")

    model_dir = Path(__file__).resolve().parent
    model_path = model_dir / "model.pkl"

    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    # Save feature order for predict.py
    meta_path = model_dir / "model_meta.pkl"
    with open(meta_path, "wb") as f:
        pickle.dump({"features": FEATURE_COLUMNS, "model_type": model_type}, f)

    print(f"Model saved to {model_path}")


if __name__ == "__main__":
    main()
