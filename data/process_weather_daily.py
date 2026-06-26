import pandas as pd

# Load weather data
df = pd.read_csv("weather_clean.csv")

# Convert time column to datetime
df["valid_time"] = pd.to_datetime(df["valid_time"])

# Create date column
df["date"] = df["valid_time"].dt.date

# Daily average temperature
daily_weather = df.groupby("date").agg({
    "t2m": "mean",
    "tp": "sum"
}).reset_index()

daily_weather.to_csv("weather_daily.csv", index=False)

print("✅ weather_daily.csv created successfully!")
