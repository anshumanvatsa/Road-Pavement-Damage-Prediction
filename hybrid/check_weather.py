import pandas as pd

df = pd.read_csv("../data/weather_daily.csv")
print("Columns:", df.columns.tolist())
print("\nFirst 5 rows:")
print(df.head())
print("\nStats:")
print(df.describe())