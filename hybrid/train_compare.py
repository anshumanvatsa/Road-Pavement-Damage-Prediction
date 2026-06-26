import pandas as pd
import numpy as np
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor
from sklearn.ensemble import GradientBoostingRegressor
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import joblib
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv("daily_hybrid_dataset.csv")
df = df.sort_values("date").reset_index(drop=True)
print(f"Dataset shape: {df.shape}")
print(f"Severity variance: {df['severity_index'].var():.6f}")
print(f"Target variance:   {df['target_6m'].var():.6f}")

# ── Feature groups ───────────────────────────────────────────────────
weather_features = [
    "temperature_c", "rainfall_mm",
    "rainfall_7d", "rainfall_30d", "temp_ma7", "temp_stress"
]
severity_features = [
    "severity_index",
    "severity_lag7", "severity_lag30",
    "severity_ma7", "severity_ma30"
]
hybrid_features = weather_features + severity_features + [
    "traffic_volume", "traffic_ma30", "traffic_norm"
]

target = "target_6m"

# Time-series split (no data leakage)
split = int(len(df) * 0.8)
print(f"Train: {split} rows | Test: {len(df)-split} rows")

results = {}

for name, feats in [
    ("Weather Only",   weather_features),
    ("Severity Only",  severity_features),
    ("Hybrid (Ours)",  hybrid_features),
]:
    X = df[feats]
    y = df[target]
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]

    model = XGBRegressor(
        n_estimators=200,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    pred = model.predict(X_test)

    r2   = r2_score(y_test, pred)
    mae  = mean_absolute_error(y_test, pred)
    rmse = np.sqrt(mean_squared_error(y_test, pred))

    results[name] = {"R2": r2, "MAE": mae, "RMSE": rmse,
                     "pred": pred, "y_test": y_test.values, "model": model}
    print(f"\n{name}\n  R²={r2:.4f}  MAE={mae:.4f}  RMSE={rmse:.4f}")

print("\n" + "="*55)
print(f"{'Model':<20} {'R²':>8} {'MAE':>8} {'RMSE':>8}")
print("="*55)
for name, m in results.items():
    print(f"{name:<20} {m['R2']:>8.4f} {m['MAE']:>8.4f} {m['RMSE']:>8.4f}")

# ── Save best model ──────────────────────────────────────────────────
joblib.dump({
    "model": results["Hybrid (Ours)"]["model"],
    "features": hybrid_features
}, "hybrid_model.pkl")
print("\n✅ hybrid_model.pkl saved")

# ── Figure 1: Model comparison bar chart ────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(13, 5))
model_names = list(results.keys())
colors = ["#3498db", "#e67e22", "#27ae60"]

for ax, metric in zip(axes, ["R2", "MAE", "RMSE"]):
    vals = [results[m][metric] for m in model_names]
    bars = ax.bar(model_names, vals, color=colors, edgecolor="black", linewidth=0.6)
    ax.set_title({"R2": "R² Score (↑ better)",
                  "MAE": "MAE (↓ better)",
                  "RMSE": "RMSE (↓ better)"}[metric], fontweight="bold")
    ax.set_xticklabels(model_names, rotation=12, ha="right")
    if metric == "R2":
        ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.001 if v >= 0 else bar.get_height() - 0.02,
                f"{v:.3f}", ha="center", fontsize=9, fontweight="bold")

plt.suptitle("Hybrid Road Deterioration Prediction — Model Comparison\n(6-Month Forecast Horizon)",
             fontweight="bold")
plt.tight_layout()
plt.savefig("model_comparison.png", dpi=150, bbox_inches="tight")
print("✅ model_comparison.png saved")

# ── Figure 2: Actual vs Predicted ───────────────────────────────────
y_test_h = results["Hybrid (Ours)"]["y_test"]
pred_h   = results["Hybrid (Ours)"]["pred"]

fig2, ax2 = plt.subplots(figsize=(11, 4))
ax2.plot(y_test_h, "b-o", linewidth=1.5, markersize=4, label="Actual Severity (6m ahead)")
ax2.plot(pred_h, "r--s", linewidth=1.5, markersize=4, label="Hybrid Predicted")
ax2.fill_between(range(len(y_test_h)), y_test_h, pred_h, alpha=0.15, color="red")
ax2.set_xlabel("Test Sample Index (Days)")
ax2.set_ylabel("Road Severity Index")
ax2.set_title("Hybrid Digital Twin — 6-Month Road Severity Forecast")
ax2.legend()
ax2.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("actual_vs_predicted.png", dpi=150)
print("✅ actual_vs_predicted.png saved")

# ── Figure 3: Feature importance ────────────────────────────────────
fi = results["Hybrid (Ours)"]["model"].feature_importances_
feat_df = pd.DataFrame({"Feature": hybrid_features, "Importance": fi})\
            .sort_values("Importance", ascending=True)

fig3, ax3 = plt.subplots(figsize=(8, 6))
colors_fi = ["#27ae60" if i >= len(feat_df)-5 else "#aed6f1"
             for i in range(len(feat_df))]
ax3.barh(feat_df["Feature"], feat_df["Importance"],
         color=colors_fi, edgecolor="black", linewidth=0.4)
ax3.set_xlabel("XGBoost Feature Importance")
ax3.set_title("Feature Importance — Hybrid Model")
ax3.grid(True, alpha=0.3, axis="x")
plt.tight_layout()
plt.savefig("feature_importance.png", dpi=150)
print("✅ feature_importance.png saved")
