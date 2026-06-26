import pandas as pd
import numpy as np

np.random.seed(42)
dates = pd.date_range("2022-01-01", "2022-12-31", freq="D")

# Realistic India monthly temperature (Celsius) pattern
monthly_temp_c = {
    1: 15, 2: 18, 3: 24, 4: 30, 5: 35,
    6: 33, 7: 30, 8: 29, 9: 30, 10: 27,
    11: 22, 12: 17
}
# Realistic India monthly rainfall (mm/day) - monsoon pattern
monthly_rain = {
    1: 0.5, 2: 0.5, 3: 0.3, 4: 0.3, 5: 1.0,
    6: 8.0, 7: 12.0, 8: 11.0, 9: 7.0, 10: 2.5,
    11: 1.0, 12: 0.5
}

t2m_k, tp_m = [], []
for d in dates:
    base_c = monthly_temp_c[d.month]
    noise = np.random.normal(0, 1.5)
    t2m_k.append(base_c + 273.15 + noise)
    
    base_rain = monthly_rain[d.month]
    rain = max(0, np.random.exponential(base_rain))
    tp_m.append(rain / 1000)  # convert mm to metres (ERA5 unit)

df = pd.DataFrame({"date": dates.strftime("%Y-%m-%d"), "t2m": t2m_k, "tp": tp_m})
df.to_csv("../data/weather_daily.csv", index=False)
print("✅ weather_daily.csv replaced with realistic India values")
print(df.describe())