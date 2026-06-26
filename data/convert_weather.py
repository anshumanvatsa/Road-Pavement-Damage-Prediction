import xarray as xr
import pandas as pd

# Open NetCDF file (NOT GRIB anymore)
ds = xr.open_dataset("weather_2022.nc")

print("Dataset loaded successfully")

# Convert to DataFrame
df = ds.to_dataframe().reset_index()

# Keep only useful columns
# (your dataset may contain latitude & longitude columns)
print("Columns in weather file:", df.columns)

# Save full clean weather data
df.to_csv("weather_clean.csv", index=False)

print("✅ weather_clean.csv created successfully")
