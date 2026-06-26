import pandas as pd

# Load dataset
df = pd.read_csv("../data/RS_Session_262_AS_188_A.csv")

# Clean column names
df.columns = df.columns.str.strip()

print("Columns found:", df.columns.tolist())

# Rename correctly using ACTUAL column name
df = df.rename(columns={
    "Month - 2022-23": "month",
    "FASTag Transaction Count": "traffic_volume"
})

# Add year manually
df["year"] = 2022

# Convert month names to numbers
month_map = {
    "January":1,"February":2,"March":3,"April":4,
    "May":5,"June":6,"July":7,"August":8,
    "September":9,"October":10,"November":11,"December":12
}

df["month"] = df["month"].map(month_map)

# Keep required columns
df = df[["year","month","traffic_volume"]]

df.to_csv("traffic_monthly.csv", index=False)

print("Traffic monthly created successfully.")