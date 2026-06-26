import xarray as xr
import pandas as pd

# Load datasets
temp_ds = xr.open_dataset("../data/c8c14aacc047870d53d008058653b466/data_stream-oper_stepType-instant.nc")
rain_ds = xr.open_dataset("../data/c8c14aacc047870d53d008058653b466/data_stream-oper_stepType-accum.nc")

# Select India location (Delhi)
temp_sel = temp_ds.sel(latitude=28.6, longitude=77.2, method="nearest")
rain_sel = rain_ds.sel(latitude=28.6, longitude=77.2, method="nearest")

# Convert to dataframe
df_temp = temp_sel.to_dataframe().reset_index()
df_rain = rain_sel.to_dataframe().reset_index()

# FIX: rename valid_time → time
df_temp = df_temp.rename(columns={"valid_time": "time"})
df_rain = df_rain.rename(columns={"valid_time": "time"})

# Merge
df = pd.merge(df_temp, df_rain, on="time")

# Convert temperature
df["t2m_c"] = df["t2m"] - 273.15

# 🔥 IMPORTANT: Convert hourly → DAILY
df["date"] = pd.to_datetime(df["time"]).dt.date

df_daily = df.groupby("date").agg({
    "t2m_c": "mean",
    "tp": "sum"
}).reset_index()

# Save
df_daily.to_csv("../data/weather_daily.csv", index=False)

print("✅ weather_daily.csv created")
print(df_daily.describe())