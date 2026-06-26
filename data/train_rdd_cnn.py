import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import copy
import os
from torch.cuda.amp import GradScaler, autocast


def main():

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Using device:", device)

    # =============================
    # STRONG BUT STABLE AUGMENTATION
    # =============================
    train_transform = transforms.Compose([
        transforms.Resize((320, 320)),
        transforms.RandomResizedCrop(300),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(25),
        transforms.ColorJitter(0.3, 0.3, 0.3, 0.2),
        transforms.RandomPerspective(distortion_scale=0.2, p=0.3),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    val_transform = transforms.Compose([
        transforms.Resize((300, 300)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    train_data = datasets.ImageFolder("rdd_train_cnn", transform=train_transform)
    val_data = datasets.ImageFolder("rdd_val_cnn", transform=val_transform)

    # =============================
    # CLASS WEIGHTS (IMBALANCE FIX)
    # =============================
    class_counts = []
    for i in range(len(train_data.classes)):
        class_counts.append(len(os.listdir(os.path.join("rdd_train_cnn", str(i)))))

    class_counts = np.array(class_counts)
    class_weights = 1.0 / class_counts
    class_weights = torch.tensor(class_weights, dtype=torch.float).to(device)

    print("Class counts:", class_counts)
    print("Class weights:", class_weights)

    # Smaller batch for RAM safety
    train_loader = DataLoader(train_data, batch_size=8, shuffle=True,
                              num_workers=0, pin_memory=True)

    val_loader = DataLoader(val_data, batch_size=8,
                            num_workers=0, pin_memory=True)

    # =============================
    # MODEL: EfficientNet-B3
    # =============================
    model = models.efficientnet_b3(
        weights=models.EfficientNet_B3_Weights.DEFAULT
    )

    model.classifier[1] = nn.Linear(model.classifier[1].in_features, 5)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = optim.AdamW(model.parameters(), lr=0.0003, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=40)

    scaler = GradScaler()

    num_epochs = 40
    best_acc = 0
    best_model_wts = copy.deepcopy(model.state_dict())
    early_stop_counter = 0

    train_losses, val_losses = [], []
    train_accs, val_accs = [], []

    for epoch in range(num_epochs):

        # ================= TRAIN =================
        model.train()
        running_loss, correct, total = 0, 0, 0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()

            with autocast():
                outputs = model(images)
                loss = criterion(outputs, labels)

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            running_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        scheduler.step()

        train_loss = running_loss / len(train_loader)
        train_acc = correct / total

        train_losses.append(train_loss)
        train_accs.append(train_acc)

        # ================= VALIDATION =================
        model.eval()
        val_loss, correct, total = 0, 0, 0
        all_preds, all_labels = [], []

        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)

                with autocast():
                    outputs = model(images)
                    loss = criterion(outputs, labels)

                val_loss += loss.item()
                _, predicted = torch.max(outputs, 1)

                total += labels.size(0)
                correct += (predicted == labels).sum().item()

                all_preds.extend(predicted.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())

        val_loss /= len(val_loader)
        val_acc = correct / total

        val_losses.append(val_loss)
        val_accs.append(val_acc)

        print(f"Epoch {epoch+1}/{num_epochs}")
        print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}")
        print(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
        print("-" * 50)

        # Save best model
        if val_acc > best_acc:
            best_acc = val_acc
            best_model_wts = copy.deepcopy(model.state_dict())
            early_stop_counter = 0
        else:
            early_stop_counter += 1

        # Early stopping
        if early_stop_counter >= 8:
            print("Early stopping triggered")
            break

    model.load_state_dict(best_model_wts)
    torch.save(model.state_dict(), "best_rdd_model.pth")
    print("Best model saved with accuracy:", best_acc)

    # ================= JOURNAL PLOTS =================
    plt.figure()
    plt.plot(train_losses, label="Train Loss")
    plt.plot(val_losses, label="Val Loss")
    plt.legend()
    plt.title("Loss Curve")
    plt.savefig("loss_curve.png")
    plt.close()

    plt.figure()
    plt.plot(train_accs, label="Train Accuracy")
    plt.plot(val_accs, label="Val Accuracy")
    plt.legend()
    plt.title("Accuracy Curve")
    plt.savefig("accuracy_curve.png")
    plt.close()

    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.title("Confusion Matrix")
    plt.savefig("confusion_matrix.png")
    plt.close()

    report = classification_report(all_labels, all_preds)
    with open("classification_report.txt", "w") as f:
        f.write(report)

    print("All journal plots saved successfully!")


if __name__ == "__main__":
    main()