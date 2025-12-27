#!/usr/bin/env python3
"""
Verification Script - Train a small model and detect poisoning

This script implements the "local trap" from Phase 1:
1. Create a mini-dataset (clean + poisoned images)
2. Train a small ResNet-18
3. Run detection to verify the poison worked
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
from torchvision.models import ResNet18_Weights
from pathlib import Path
from PIL import Image
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'poison-core'))
from radioactive_poison import RadioactiveDetector
import json
from tqdm import tqdm


class ImageDataset(Dataset):
    """Simple dataset for clean/poisoned image classification."""
    
    def __init__(self, image_folder, transform=None):
        self.image_folder = Path(image_folder)
        self.transform = transform
        
        # Find all images
        image_extensions = {'.jpg', '.jpeg', '.png'}
        self.images = [f for f in self.image_folder.rglob('*') 
                       if f.suffix.lower() in image_extensions]
        
        # Assign labels based on subfolder (0=clean, 1=poisoned)
        self.labels = []
        for img in self.images:
            if 'poisoned' in str(img.parent):
                self.labels.append(1)
            else:
                self.labels.append(0)
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        img_path = self.images[idx]
        image = Image.open(img_path).convert('RGB')
        label = self.labels[idx]
        
        if self.transform:
            image = self.transform(image)
        
        return image, label


def train_test_model(
    data_folder: str,
    epochs: int = 10,
    batch_size: int = 32,
    lr: float = 0.001,
    device: str = 'cpu'
):
    """
    Train a small ResNet-18 on the dataset.
    
    Args:
        data_folder: Folder containing 'clean' and 'poisoned' subfolders
        epochs: Number of training epochs
        batch_size: Batch size
        lr: Learning rate
        device: 'cpu' or 'cuda'
    """
    print("🧪 Verification - Training test model")
    print("=" * 60)
    
    # Data transforms
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    # Load dataset
    dataset = ImageDataset(data_folder, transform=transform)
    print(f"Dataset: {len(dataset)} images")
    
    # Split into train/test
    train_size = int(0.8 * len(dataset))
    test_size = len(dataset) - train_size
    train_dataset, test_dataset = torch.utils.data.random_split(
        dataset, [train_size, test_size]
    )
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    # Initialize model
    model = models.resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, 2)  # Binary classification
    model = model.to(device)
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    # Training loop
    print(f"\nTraining for {epochs} epochs...")
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        pbar = tqdm(train_loader, desc=f'Epoch {epoch+1}/{epochs}')
        for images, labels in pbar:
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            pbar.set_postfix({
                'loss': f'{running_loss/len(train_loader):.3f}',
                'acc': f'{100.*correct/total:.1f}%'
            })
    
    # Evaluate
    model.eval()
    correct = 0
    total = 0
    
    print("\nEvaluating...")
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
    
    accuracy = 100. * correct / total
    print(f"Test Accuracy: {accuracy:.2f}%")
    
    # Save model
    model_path = "verification/trained_model.pth"
    torch.save(model, model_path)
    print(f"\n✅ Model saved to {model_path}")
    
    return model


def run_detection(
    model_path: str,
    signature_path: str,
    test_images_folder: str,
    threshold: float = 0.1
):
    """
    Run radioactive detection on the trained model.
    """
    print("\n" + "=" * 60)
    print("🔍 Running Radioactive Detection")
    print("=" * 60)
    
    # Load model (PyTorch 2.6+ compatibility)
    model = torch.load(model_path, weights_only=False)
    # Remove final classification layer to get feature extractor
    model = nn.Sequential(*list(model.children())[:-1])
    
    # Find test images
    test_path = Path(test_images_folder)
    image_extensions = {'.jpg', '.jpeg', '.png'}
    test_images = [str(f) for f in test_path.rglob('*') 
                   if f.suffix.lower() in image_extensions][:20]  # Use 20 test images
    
    print(f"Model: {model_path}")
    print(f"Signature: {signature_path}")
    print(f"Test images: {len(test_images)}")
    
    # Run detection
    detector = RadioactiveDetector(signature_path)
    is_poisoned, confidence = detector.detect(model, test_images, threshold)
    
    print(f"\n{'🎯' if is_poisoned else '❌'} Detection Result:")
    print(f"   Poisoned: {is_poisoned}")
    print(f"   Confidence Score: {confidence:.6f}")
    print(f"   Threshold: {threshold}")
    
    if is_poisoned:
        print(f"\n✅ SUCCESS! The poison signature was detected in the trained model!")
        print(f"   This proves the radioactive marking works.")
        print(f"\n   What this means:")
        print(f"   • The model learned from your poisoned images")
        print(f"   • Your unique signature is embedded in the model's weights")
        print(f"   • You can prove this model trained on your data")
    else:
        print(f"\n⚠️  Signature not detected. Possible reasons:")
        print(f"   • Epsilon too small (try increasing to 0.02-0.05)")
        print(f"   • Not enough poisoned images in training set")
        print(f"   • Model architecture mismatch")
    
    return is_poisoned, confidence


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Verify radioactive poisoning')
    parser.add_argument('--data', default='verification/test_data', 
                       help='Folder with clean/poisoned subfolders')
    parser.add_argument('--signature', default='verification/test_signature.json',
                       help='Signature file')
    parser.add_argument('--epochs', type=int, default=5,
                       help='Training epochs')
    parser.add_argument('--device', default='cpu', choices=['cpu', 'cuda'])
    
    args = parser.parse_args()
    
    # Step 1: Train model
    model = train_test_model(
        args.data,
        epochs=args.epochs,
        device=args.device
    )
    
    # Step 2: Run detection
    run_detection(
        'verification/trained_model.pth',
        args.signature,
        args.data,
        threshold=0.05
    )
