import os

# Mapping dictionary
class_map = {
    0: 0,  # D00 -> Minor
    1: 0,  # D10 -> Minor
    2: 1,  # D20 -> Moderate
    3: 2,  # D40 -> Severe
    4: 2   # D43 -> Severe
}

# Change this path to your dataset root
dataset_root = r"D:\Predictive_Project\data\archive (3)\RDD_SPLIT"

for split in ["train", "val", "test"]:
    label_path = os.path.join(dataset_root, split, "labels")

    for file in os.listdir(label_path):
        if file.endswith(".txt"):
            file_path = os.path.join(label_path, file)

            with open(file_path, "r") as f:
                lines = f.readlines()

            new_lines = []
            for line in lines:
                parts = line.strip().split()
                old_class = int(parts[0])
                new_class = class_map[old_class]
                parts[0] = str(new_class)
                new_lines.append(" ".join(parts) + "\n")

            with open(file_path, "w") as f:
                f.writelines(new_lines)

print("✅ Conversion to 3 classes completed.")