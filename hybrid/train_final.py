import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import joblib

df = pd.read_csv("final_dataset.csv")
print("Dataset:\n", df.head())

features_weather = ["temp_avg_c", "temp_max_c", "rainfall_total"]
features_vision  = ["severity_index"]
features_traffic = ["traffic_count"]
features_all     = features_weather + features_vision + features_traffic
target           = "target_severity"

def evaluate(X, y, name):
    loo = LeaveOneOut()
    preds, actuals = [], []
    for tr, te in loo.split(X):
        model = GradientBoostingRegressor(n_estimators=100, max_depth=2, random_state=42)
        model.fit(X[tr], y[tr])
        preds.append(model.predict(X[te])[0])
        actuals.append(y[te][0])
    r2  = r2_score(actuals, preds)
    mae = mean_absolute_error(actuals, preds)
    rmse = np.sqrt(mean_squared_error(actuals, preds))
    print(f"\n{name}")
    print(f"  R²   = {r2:.4f}")
    print(f"  MAE  = {mae:.4f}")
    print(f"  RMSE = {rmse:.4f}")
    return r2, mae, rmse, preds, actuals

X = df[features_all].values
y = df[target].values

r2_w,  mae_w,  rmse_w,  _,     _       = evaluate(df[features_weather].values, y, "Weather Only")
r2_v,  mae_v,  rmse_v,  _,     _       = evaluate(df[features_vision].values,  y, "Vision (YOLO) Only")
r2_h,  mae_h,  rmse_h,  preds, actuals = evaluate(X,                           y, "Hybrid (Ours)")

# --- Train final model on all data and save ---
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
final_model = GradientBoostingRegressor(n_estimators=100, max_depth=2, random_state=42)
final_model.fit(X_scaled, y)
joblib.dump({"model": final_model, "scaler": scaler, "features": features_all}, "hybrid_model.pkl")
print("\n✅ hybrid_model.pkl saved")

# --- Comparison chart ---
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
models = ["Weather Only", "Vision Only", "Hybrid (Ours)"]
r2s   = [r2_w, r2_v, r2_h]
maes  = [mae_w, mae_v, mae_h]
colors = ["#e74c3c", "#f39c12", "#27ae60"]

axes[0].bar(models, r2s, color=colors)
axes[0].set_title("R² Score (higher = better)")
axes[0].set_ylabel("R²")
axes[0].axhline(0, color="black", linewidth=0.8, linestyle="--")

axes[1].bar(models, maes, color=colors)
axes[1].set_title("MAE (lower = better)")
axes[1].set_ylabel("MAE")

plt.tight_layout()
plt.savefig("model_comparison.png", dpi=150)
print("✅ model_comparison.png saved")

# --- Actual vs Predicted ---
plt.figure(figsize=(8, 5))
plt.plot(actuals, "b-o", label="Actual")
plt.plot(preds,   "r--s", label="Predicted (Hybrid)")
plt.title("Hybrid Model: Actual vs Predicted Severity")
plt.xlabel("Sample")
plt.ylabel("Severity Index")
plt.legend()
plt.savefig("actual_vs_predicted.png", dpi=150)
print("✅ actual_vs_predicted.png saved")