import os

dataset_root = r"D:\Predictive_Project\data\archive (3)\RDD_SPLIT"

invalid_found = False

for split in ["train", "val", "test"]:
    label_path = os.path.join(dataset_root, split, "labels")

    for file in os.listdir(label_path):
        if file.endswith(".txt"):
            file_path = os.path.join(label_path, file)

            with open(file_path, "r") as f:
                lines = f.readlines()

            for line in lines:
                parts = line.strip().split()
                if len(parts) == 0:
                    continue

                class_id = int(parts[0])

                if class_id not in [0, 1, 2]:
                    print(f"❌ Invalid class {class_id} in {file_path}")
                    invalid_found = True

if not invalid_found:
    print("✅ All labels are valid (0,1,2 only)")