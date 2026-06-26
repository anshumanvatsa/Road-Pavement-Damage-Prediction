import os
import shutil
import pandas as pd

def organize_split(split_name):
    labels_path = f"archive (3)/RDD_SPLIT/{split_name}/labels"
    images_path = f"archive (3)/RDD_SPLIT/{split_name}/images"
    output_path = f"rdd_{split_name}_cnn"

    os.makedirs(output_path, exist_ok=True)

    data = []

    for file in os.listdir(labels_path):
        if file.endswith(".txt"):
            file_path = os.path.join(labels_path, file)

            with open(file_path, "r") as f:
                lines = f.readlines()

            for line in lines:
                class_id = int(line.split()[0])
                image_name = file.replace(".txt", ".jpg")
                data.append([image_name, class_id])

    df = pd.DataFrame(data, columns=["image_name", "damage_class"])

    classes = df["damage_class"].unique()
    for cls in classes:
        os.makedirs(os.path.join(output_path, str(cls)), exist_ok=True)

    for _, row in df.iterrows():
        img_name = row["image_name"]
        cls = str(row["damage_class"])

        src = os.path.join(images_path, img_name)
        dst = os.path.join(output_path, cls, img_name)

        if os.path.exists(src):
            shutil.copy(src, dst)

    print(f"✅ {split_name} dataset organized successfully!")

# Organize both train and val
organize_split("train")
organize_split("val")
