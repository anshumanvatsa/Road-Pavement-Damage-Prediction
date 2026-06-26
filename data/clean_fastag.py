import pandas as pd
import calendar

# Load file
df = pd.read_csv("RS_Session_262_AS_188_A.csv")

print("Columns in file:", df.columns)

# Rename month column correctly
df.rename(columns={"Month - 2022-23": "Month"}, inplace=True)

# Remove grand total row
df = df[df["Month"] != "Grand Total"]

# Month mapping
month_map = {
    "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9,
    "October": 10, "November": 11, "December": 12,
    "January": 1, "February": 2, "March": 3
}

df["Month_Num"] = df["Month"].map(month_map)

# Financial year 2022-23
# April–Dec → 2022
# Jan–Mar → 2023
df["Year"] = df["Month_Num"].apply(lambda x: 2022 if x >= 4 else 2023)

df["Days"] = df.apply(
    lambda row: calendar.monthrange(row["Year"], row["Month_Num"])[1],
    axis=1
)

df["traffic_volume"] = df["FASTag Transaction Count"] / df["Days"]

df["date"] = pd.to_datetime(
    df["Year"].astype(str) + "-" +
    df["Month_Num"].astype(str) + "-01"
)

final_df = df[["date", "traffic_volume"]]

final_df.to_csv("traffic_clean.csv", index=False)

print("✅ traffic_clean.csv created successfully")
