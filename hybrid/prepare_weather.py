import pandas as pd

# Load daily weather
df = pd.read_csv("../data/weather_daily.csv")

# Convert date column
df["date"] = pd.to_datetime(df["date"])

# Extract year and month
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month

# Monthly aggregation
monthly_weather = df.groupby(["year", "month"]).agg({
    "t2m": "mean",      # average temperature
    "tp": "sum"         # total rainfall
}).reset_index()

monthly_weather.to_csv("weather_monthly.csv", index=False)

print("Weather monthly aggregation done.")