import pandas as pd
import os

keywords = [
    "AADT",
    "Average Daily Traffic",
    "Annual Average",
    "ADT",
    "Traffic Volume"
]

for file in os.listdir():
    if file.endswith(".csv"):
        df = pd.read_csv(file)
        text = df.astype(str).apply(lambda x: x.str.lower()).values.flatten()
        for keyword in keywords:
            if any(keyword.lower() in str(cell) for cell in text):
                print("Possible traffic table found in:", file)
                break
