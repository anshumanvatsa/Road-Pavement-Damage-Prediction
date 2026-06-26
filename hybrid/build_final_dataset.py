import pandas as pd
import numpy as np

np.random.seed(42)

# Load ERA5 weather (your correctly downloaded one)
weather = pd.read_csv("../data/weather_daily.csv")
weather["date"] = pd.to_datetime(weather["date"])
weather = weather.sort_values("date").reset_index(drop=True)

# Temperature column — handle both possible column names
if "t2m_c" in weather.columns:
    weather["temperature_c"] = weather["t2m_c"]
elif "t2m" in weather.columns:
    weather["temperature_c"] = weather["t2m"] - 273.15  # Kelvin to Celsius

# Monthly traffic (FASTag 2022-23, April=month4 ... March=month3)
monthly_traffic = {
    4: 227688304, 5: 242408119, 6: 235289382,
    7: 224006604, 8: 229119617, 9: 218365188,
    10: 237783149, 11: 239426702, 12: 257885207,
    1: 250983877, 2: 240638035, 3: 254649641
}
weather["month"] = weather["date"].dt.month
weather["traffic_volume"] = weather["month"].map(monthly_traffic)

# Normalize traffic to 0-1 scale
t_min, t_max = min(monthly_traffic.values()), max(monthly_traffic.values())
weather["traffic_norm"] = (weather["traffic_volume"] - t_min) / (t_max - t_min)

# Normalize rainfall to 0-1 (daily tp in metres, scale to mm)
weather["rainfall_mm"] = weather["tp"] * 1000  # metres -> mm
rain_99 = weather["rainfall_mm"].quantile(0.99)
weather["rainfall_norm"] = (weather["rainfall_mm"] / rain_99).clip(0, 1)

# Temperature stress: deviations from 20°C (optimal), normalized
weather["temp_stress"] = (np.abs(weather["temperature_c"] - 20) / 20).clip(0, 1)

# ── CAUSAL SEVERITY MODEL (physically grounded) ─────────────────────
# Road damage accumulates from: rainfall (erosion), heat stress (cracking),
# traffic load. This matches pavement engineering literature.
severity = []
for i in range(len(weather)):
    prev = severity[i-1] if i > 0 else 0.20
    increment = (
        0.35 * weather.loc[i, "rainfall_norm"]
        + 0.25 * weather.loc[i, "temp_stress"]
        + 0.20 * weather.loc[i, "traffic_norm"]
    )
    # Natural recovery / maintenance factor (slight regression to mean)
    new_val = 0.75 * prev + 0.25 * increment
    severity.append(float(np.clip(new_val, 0.05, 0.95)))

weather["severity_index"] = severity

# Rolling features
weather["severity_lag7"]  = weather["severity_index"].shift(7)
weather["severity_lag30"] = weather["severity_index"].shift(30)
weather["severity_ma7"]   = weather["severity_index"].rolling(7).mean()
weather["severity_ma30"]  = weather["severity_index"].rolling(30).mean()
weather["rainfall_7d"]    = weather["rainfall_mm"].rolling(7).sum()
weather["rainfall_30d"]   = weather["rainfall_mm"].rolling(30).sum()
weather["temp_ma7"]       = weather["temperature_c"].rolling(7).mean()
weather["traffic_ma30"]   = weather["traffic_volume"].rolling(30).mean()

# ── TARGET: severity 180 days ahead (6 months) ──────────────────────
weather["target_6m"] = weather["severity_index"].shift(-180)

# Drop NaN rows
weather = weather.dropna()
print(f"Dataset rows after dropna: {len(weather)}")
print(f"Severity range: {weather['severity_index'].min():.3f} – {weather['severity_index'].max():.3f}")
print(f"Target range:   {weather['target_6m'].min():.3f} – {weather['target_6m'].max():.3f}")

cols = [
    "date",
    "temperature_c", "rainfall_mm", "traffic_volume",
    "temp_stress", "rainfall_norm", "traffic_norm",
    "severity_index",
    "severity_lag7", "severity_lag30",
    "severity_ma7", "severity_ma30",
    "rainfall_7d", "rainfall_30d",
    "temp_ma7", "traffic_ma30",
    "target_6m"
]

weather[cols].to_csv("daily_hybrid_dataset.csv", index=False)
print("✅ daily_hybrid_dataset.csv saved")
print(weather[["temperature_c", "rainfall_mm", "severity_index", "target_6m"]].describe().round(3))