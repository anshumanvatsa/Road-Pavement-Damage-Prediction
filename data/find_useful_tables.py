import pandas as pd
import os

folder = "."

keywords = ["AADT", "Average", "Traffic", "Truck", "Bus", "Commercial"]

for file in os.listdir(folder):
    if file.endswith(".csv"):
        try:
            df = pd.read_csv(file)
            text = df.to_string().lower()

            for word in keywords:
                if word.lower() in text:
                    print(f"Match found in {file}")
                    break
        except:
            continue
