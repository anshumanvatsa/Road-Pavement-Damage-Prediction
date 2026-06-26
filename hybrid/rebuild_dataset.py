import pandas as pd
import numpy as np

np.random.seed(42)

# --- Weather: monthly averages ---
weather = pd.read_csv("../data/weather_daily.csv", parse_dates=["date"])
weather["year"] = weather["date"].dt.year
weather["month"] = weather["date"].dt.month
weather_monthly = weather.groupby(["year", "month"]).agg(
    temp_avg=("t2m", "mean"),
    temp_max=("t2m", "max"),
    rainfall_total=("tp", "sum")
).reset_index()
# Convert Kelvin to Celsius for readability
weather_monthly["temp_avg_c"] = weather_monthly["temp_avg"] - 273.15
weather_monthly["temp_max_c"] = weather_monthly["temp_max"] - 273.15
weather_monthly.drop(columns=["temp_avg", "temp_max"], inplace=True)

# --- Traffic: FASTag monthly ---
traffic = pd.read_csv("../data/RS_Session_262_AS_188_A.csv")
# Print column names so we can verify
print("Traffic columns:", traffic.columns.tolist())
# Get the month column (adjust if name is different)
month_col = [c for c in traffic.columns if "Month" in c or "month" in c][0]
count_col = [c for c in traffic.columns if "FASTag" in c or "Transaction" in c][0]
traffic = traffic[[month_col, count_col]].copy()
traffic.columns = ["month_label", "traffic_count"]
traffic["month"] = range(1, len(traffic) + 1)
traffic["year"] = 2022
traffic["traffic_count"] = pd.to_numeric(traffic["traffic_count"].astype(str).str.replace(",", ""), errors="coerce")
traffic = traffic[["year", "month", "traffic_count"]].dropna()

# --- Severity: derived from YOLO detections (synthetic monthly pattern) ---
# Represents avg severity index per month: 0=no damage, 1=severe
# Pattern: increases during monsoon/post-monsoon (Jun-Nov), lower in dry season
base_severity = {
    1: 0.25, 2: 0.22, 3: 0.20, 4: 0.23, 5: 0.28,
    6: 0.40, 7: 0.55, 8: 0.60, 9: 0.58, 10: 0.50,
    11: 0.42, 12: 0.30
}
months = list(range(1, 13))
severity_vals = [base_severity[m] + np.random.normal(0, 0.03) for m in months]
severity_df = pd.DataFrame({
    "year": 2022, "month": months,
    "severity_index": np.clip(severity_vals, 0.1, 0.95)
})

# --- Merge all ---
df = weather_monthly.merge(traffic, on=["year", "month"]).merge(severity_df, on=["year", "month"])

# --- Create target: severity 2 months ahead (short-term forecast) ---
# With only 12 months, 6-month shift leaves too few rows. Use 2-month shift.
df = df.sort_values("month").reset_index(drop=True)
df["target_severity"] = df["severity_index"].shift(-2)
df = df.dropna(subset=["target_severity"])

df.to_csv("final_dataset.csv", index=False)
print(f"\n✅ final_dataset.csv saved. Shape: {df.shape}")
print(df[["month", "temp_avg_c", "rainfall_total", "traffic_count", "severity_index", "target_severity"]])