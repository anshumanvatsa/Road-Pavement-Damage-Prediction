import os
import pandas as pd

base_path = "archive (3)/RDD_SPLIT/train/labels"

data = []

for file in os.listdir(base_path):
    if file.endswith(".txt"):
        file_path = os.path.join(base_path, file)

        with open(file_path, "r") as f:
            lines = f.readlines()

            for line in lines:
                class_id = int(line.split()[0])
                data.append([file.replace(".txt", ".jpg"), class_id])

df = pd.DataFrame(data, columns=["image_name", "damage_class"])

df.to_csv("rdd_labels.csv", index=False)

print("✅ rdd_labels.csv created")
