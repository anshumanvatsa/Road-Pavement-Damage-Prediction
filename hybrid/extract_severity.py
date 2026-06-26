import os
import pandas as pd
import numpy as np

dataset_root = "../data/archive (3)/RDD_SPLIT/train/labels"

severity_counts = []

for file in os.listdir(dataset_root):
    if not file.endswith(".txt"):
        continue

    file_path = os.path.join(dataset_root, file)

    with open(file_path, "r") as f:
        lines = f.readlines()

    severity_counts.append(len(lines))

# Create 12 months artificially
months = list(range(1, 13))

data = []

for m in months:
    avg_severity = np.mean(severity_counts) * (1 + np.random.uniform(-0.2, 0.2))
    
    data.append({
        "year": 2022,
        "month": m,
        "severity_index": avg_severity
    })

df = pd.DataFrame(data)

df.to_csv("severity_monthly.csv", index=False)

print("Synthetic severity monthly created.")