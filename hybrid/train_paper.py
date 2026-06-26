import pandas as pd
import numpy as np
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import LeaveOneOut
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import joblib, warnings
warnings.filterwarnings('ignore')

df = pd.read_csv("paper_dataset.csv")
print(f"Shape: {df.shape}")
print(df[["month","severity_index","yolo_damage_score","target_2m"]])

# ── Feature groups ───────────────────────────────────────────────────
weather_feats = ["temp_avg", "temp_max", "temp_range",
                 "rainfall", "rainy_days", "rainfall_lag1"]

vision_feats  = ["yolo_damage_score", "severity_index",
                 "severity_lag1", "severity_lag2"]

traffic_feats = ["traffic"]

hybrid_feats  = weather_feats + vision_feats + traffic_feats

target = "target_2m"

def loo_evaluate(X_df, y_series, label):
    X = X_df.values
    y = y_series.values
    loo = LeaveOneOut()
    preds, actuals = [], []
    for tr, te in loo.split(X):
        m = GradientBoostingRegressor(
            n_estimators=50, max_depth=2,
            learning_rate=0.1, random_state=42
        )
        m.fit(X[tr], y[tr])
        preds.append(float(m.predict(X[te])))
        actuals.append(float(y[te]))

    r2   = r2_score(actuals, preds)
    mae  = mean_absolute_error(actuals, preds)
    rmse = np.sqrt(mean_squared_error(actuals, preds))
    print(f"\n{label}\n  R²={r2:.4f}  MAE={mae:.4f}  RMSE={rmse:.4f}")
    return r2, mae, rmse, preds, actuals

r2_w, mae_w, rmse_w, _, _         = loo_evaluate(df[weather_feats], df[target], "Weather Only")
r2_v, mae_v, rmse_v, _, _         = loo_evaluate(df[vision_feats],  df[target], "Vision (YOLO) Only")
r2_h, mae_h, rmse_h, preds, actuals = loo_evaluate(df[hybrid_feats], df[target], "Hybrid (Ours)")

print("\n" + "="*58)
print(f"{'Model':<22} {'R²':>8} {'MAE':>8} {'RMSE':>8}")
print("="*58)
print(f"{'Weather Only':<22} {r2_w:>8.4f} {mae_w:>8.4f} {rmse_w:>8.4f}")
print(f"{'Vision (YOLO) Only':<22} {r2_v:>8.4f} {mae_v:>8.4f} {rmse_v:>8.4f}")
print(f"{'Hybrid (Ours)':<22} {r2_h:>8.4f} {mae_h:>8.4f} {rmse_h:>8.4f}")

# ── Save model ───────────────────────────────────────────────────────
final = GradientBoostingRegressor(
    n_estimators=50, max_depth=2, learning_rate=0.1, random_state=42
)
final.fit(df[hybrid_feats].values, df[target].values)
joblib.dump({"model": final, "features": hybrid_feats}, "hybrid_model.pkl")
print("\n✅ hybrid_model.pkl saved")

# ── Figure 1: Model comparison ───────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(13, 5))
names  = ["Weather\nOnly", "Vision\n(YOLO) Only", "Hybrid\n(Ours)"]
r2s    = [r2_w, r2_v, r2_h]
maes   = [mae_w, mae_v, mae_h]
rmses  = [rmse_w, rmse_v, rmse_h]
colors = ["#3498db", "#e67e22", "#27ae60"]

for ax, vals, title in zip(
    axes,
    [r2s, maes, rmses],
    ["R² Score (↑ better)", "MAE (↓ better)", "RMSE (↓ better)"]
):
    bars = ax.bar(names, vals, color=colors, edgecolor="black", linewidth=0.7, width=0.5)
    ax.set_title(title, fontweight="bold", fontsize=11)
    if "R²" in title:
        ax.axhline(0, color="black", linewidth=1, linestyle="--")
    for bar, v in zip(bars, vals):
        ypos = bar.get_height() + 0.005 if v >= 0 else bar.get_height() - 0.025
        ax.text(bar.get_x() + bar.get_width()/2, ypos,
                f"{v:.3f}", ha="center", fontsize=10, fontweight="bold")

plt.suptitle("Road Deterioration Prediction — 2-Month Forecast\n"
             "Hybrid (Vision + Weather + Traffic) vs Baselines",
             fontweight="bold", fontsize=12)
plt.tight_layout()
plt.savefig("model_comparison.png", dpi=150, bbox_inches="tight")
print("✅ model_comparison.png saved")

# ── Figure 2: Actual vs Predicted ───────────────────────────────────
fig2, ax2 = plt.subplots(figsize=(10, 4))
months = df["month"].values[:len(actuals)]
ax2.plot(months, actuals, "b-o", linewidth=2, markersize=6, label="Actual Severity")
ax2.plot(months, preds,   "r--s", linewidth=2, markersize=6, label="Predicted (Hybrid)")
ax2.set_xlabel("Month")
ax2.set_ylabel("Road Severity Index")
ax2.set_title("Hybrid Digital Twin — Actual vs Predicted Road Severity")
ax2.legend(fontsize=11)
ax2.grid(True, alpha=0.3)
ax2.set_xticks(months)
plt.tight_layout()
plt.savefig("actual_vs_predicted.png", dpi=150)
print("✅ actual_vs_predicted.png saved")

# ── Figure 3: Feature importance ────────────────────────────────────
fi = final.feature_importances_
feat_df = pd.DataFrame({"Feature": hybrid_feats, "Importance": fi})\
            .sort_values("Importance", ascending=True)

fig3, ax3 = plt.subplots(figsize=(8, 6))
bar_colors = ["#27ae60" if i >= len(feat_df)-4 else "#aed6f1"
              for i in range(len(feat_df))]
ax3.barh(feat_df["Feature"], feat_df["Importance"],
         color=bar_colors, edgecolor="black", linewidth=0.4)
ax3.set_xlabel("Feature Importance (Gradient Boosting)")
ax3.set_title("Feature Importance — Hybrid Model")
ax3.grid(True, alpha=0.3, axis="x")
plt.tight_layout()
plt.savefig("feature_importance.png", dpi=150)
print("✅ feature_importance.png saved")

# ── Figure 4: Severity progression (shows digital twin concept) ──────
fig4, ax4 = plt.subplots(figsize=(10, 4))
ax4.plot(df["month"], df["severity_index"], "b-o",
         linewidth=2, markersize=5, label="Current Severity")
ax4.plot(df["month"], df["target_2m"], "r--^",
         linewidth=2, markersize=5, label="Future Severity (2 months ahead)")
ax4.fill_between(df["month"], df["severity_index"], df["target_2m"],
                 alpha=0.15, color="red", label="Deterioration zone")
ax4.set_xlabel("Month (2022)")
ax4.set_ylabel("Road Severity Index")
ax4.set_title("Road Deterioration Progression — Digital Twin Simulation")
ax4.legend(fontsize=10)
ax4.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("severity_progression.png", dpi=150)
print("✅ severity_progression.png saved")
