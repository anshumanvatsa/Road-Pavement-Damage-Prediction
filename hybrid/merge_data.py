import pandas as pd

# Load all datasets
weather = pd.read_csv("weather_monthly.csv")
severity = pd.read_csv("severity_monthly.csv")
traffic = pd.read_csv("traffic_monthly.csv")

print("Weather shape:", weather.shape)
print("Severity shape:", severity.shape)
print("Traffic shape:", traffic.shape)

# Merge weather + severity
df = weather.merge(severity, on=["year", "month"], how="inner")

# Merge traffic
df = df.merge(traffic, on=["year", "month"], how="inner")

print("Final merged shape:", df.shape)

df.to_csv("final_dataset.csv", index=False)

print("Final hybrid dataset created successfully.")