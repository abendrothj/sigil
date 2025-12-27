"""
Radioactive Data Poisoning Implementation
Based on: "Radioactive data: tracing through training" (Facebook AI Research, 2020)

Core concept: Inject a unique, imperceptible feature carrier signal into images
that persists through model training and can be detected in trained models.
"""

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import json
import hashlib
from pathlib import Path
from typing import Tuple, Optional
import secrets


class RadioactiveMarker:
    """
    Implements radioactive data marking using feature space perturbations.
    
    The key insight: Instead of perturbing pixels directly (easy to remove),
    we perturb the feature representation that the model will learn,
    making the signature baked into the model's weights.
    """
    
    def __init__(
        self,
        feature_extractor: Optional[nn.Module] = None,
        epsilon: float = 0.01,
        signature_dim: int = 512,
        device: str = 'cpu'
    ):
        """
        Args:
            feature_extractor: Pre-trained model to extract features (e.g., ResNet)
            epsilon: Perturbation strength (smaller = less visible, harder to detect)
            signature_dim: Dimension of the signature vector
            device: 'cpu' or 'cuda'
        """
        self.device = device
        self.epsilon = epsilon
        self.signature_dim = signature_dim
        
        # Use a pre-trained ResNet as feature extractor if none provided
        if feature_extractor is None:
            from torchvision.models import resnet18, ResNet18_Weights
            self.feature_extractor = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
            # Remove the final classification layer
            self.feature_extractor = nn.Sequential(*list(self.feature_extractor.children())[:-1])
        else:
            self.feature_extractor = feature_extractor
            
        self.feature_extractor.to(device)
        self.feature_extractor.eval()
        
        # Generate a unique signature vector
        self.signature = None
        
    def generate_signature(self, seed: Optional[int] = None) -> np.ndarray:
        """
        Generate a unique cryptographic signature vector.
        This is your "poison fingerprint."
        """
        if seed is None:
            seed = secrets.randbits(256)

        # Store full seed for cryptographic security
        self.seed = seed

        # NumPy requires 32-bit seed, so hash the full seed down to 32 bits
        # This preserves security while staying within NumPy's limits
        seed_32bit = int(hashlib.sha256(str(seed).encode()).hexdigest()[:8], 16)

        # Use cryptographic hash to generate deterministic but unpredictable signature
        rng = np.random.RandomState(seed_32bit)
        signature = rng.randn(self.signature_dim)
        # Normalize to unit vector
        signature = signature / np.linalg.norm(signature)

        self.signature = signature
        
        return signature
    
    def load_signature(self, signature_path: str):
        """Load a previously generated signature."""
        with open(signature_path, 'r') as f:
            data = json.load(f)
            self.signature = np.array(data['signature'])
            self.seed = data['seed']
            self.epsilon = data['epsilon']
    
    def save_signature(self, output_path: str):
        """Save signature for later detection."""
        if self.signature is None:
            raise ValueError("No signature generated yet. Call generate_signature() first.")
        
        data = {
            'signature': self.signature.tolist(),
            'seed': int(self.seed),
            'epsilon': float(self.epsilon),
            'signature_dim': int(self.signature_dim),
            'version': '1.0'
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def poison_image(
        self,
        image_path: str,
        output_path: str,
        normalize: bool = True,
        pgd_steps: int = 1,
        pgd_alpha: Optional[float] = None
    ) -> Tuple[str, dict]:
        """
        Poison a single image with the radioactive signature.

        Args:
            image_path: Path to input image
            output_path: Path to save poisoned image
            normalize: Whether to normalize the image
            pgd_steps: Number of PGD iterations (1=FGSM, 5-10=PGD for robustness)
            pgd_alpha: Step size for PGD (default: epsilon/steps)

        Returns:
            Tuple of (output_path, metadata)
        """
        if self.signature is None:
            raise ValueError("No signature loaded. Call generate_signature() or load_signature().")
        
        # Load and preprocess image
        img = Image.open(image_path).convert('RGB')
        original_size = img.size
        
        # Transform for feature extraction
        preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
        ])
        
        if normalize:
            preprocess = transforms.Compose([
                preprocess,
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
        
        img_tensor = preprocess(img).unsqueeze(0).to(self.device)
        original_tensor = img_tensor.clone().detach()

        # Set PGD parameters
        if pgd_alpha is None:
            pgd_alpha = self.epsilon / pgd_steps if pgd_steps > 1 else self.epsilon

        # Prepare signature tensor
        with torch.no_grad():
            features_temp = self.feature_extractor(img_tensor)
            features_temp = features_temp.view(features_temp.size(0), -1)

        signature_tensor = torch.tensor(
            self.signature[:features_temp.size(1)],
            dtype=torch.float32,
            device=self.device
        )

        # PGD loop (Projected Gradient Descent)
        # pgd_steps=1 is equivalent to FGSM (fast but weaker)
        # pgd_steps=5-10 is PGD (slower but more robust to compression)
        poisoned_tensor = img_tensor.clone()

        for step in range(pgd_steps):
            poisoned_tensor.requires_grad = True

            # Extract features
            with torch.enable_grad():
                features = self.feature_extractor(poisoned_tensor)
                features = features.view(features.size(0), -1)

                # Compute the direction to push features toward signature
                # This is the core "radioactive" perturbation
                loss = -torch.dot(features.squeeze(), signature_tensor)
                loss.backward()

            # Compute adversarial perturbation in pixel space
            grad = poisoned_tensor.grad.sign()
            perturbation = pgd_alpha * grad

            # Apply perturbation
            poisoned_tensor = poisoned_tensor.detach() + perturbation

            # Project back to epsilon ball around original
            delta = poisoned_tensor - original_tensor
            delta = torch.clamp(delta, -self.epsilon, self.epsilon)
            poisoned_tensor = original_tensor + delta

            # Clamp to valid pixel range
            poisoned_tensor = torch.clamp(poisoned_tensor, 0, 1)
        
        # Convert back to image
        if normalize:
            # Denormalize
            mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1).to(self.device)
            std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1).to(self.device)
            poisoned_tensor = poisoned_tensor * std + mean
        
        poisoned_img = transforms.ToPILImage()(poisoned_tensor.squeeze().cpu())
        poisoned_img = poisoned_img.resize(original_size, Image.LANCZOS)
        
        # Save
        poisoned_img.save(output_path, quality=95)
        
        metadata = {
            'original': str(image_path),
            'poisoned': str(output_path),
            'epsilon': self.epsilon,
            'signature_id': hashlib.sha256(str(self.seed).encode()).hexdigest()[:16]
        }
        
        return output_path, metadata


class RadioactiveDetector:
    """
    Detect if a model has been trained on radioactively marked data.
    """
    
    def __init__(self, signature_path: str, device: str = 'cpu'):
        """
        Args:
            signature_path: Path to the signature JSON file
            device: 'cpu' or 'cuda'
        """
        self.device = device
        
        # Load signature
        with open(signature_path, 'r') as f:
            data = json.load(f)
            self.signature = np.array(data['signature'])
            self.seed = data['seed']
            self.epsilon = data['epsilon']
    
    def detect(
        self,
        model: nn.Module,
        test_images: list,
        threshold: float = 0.1
    ) -> Tuple[bool, float]:
        """
        Detect if a model was trained on marked data.
        
        Args:
            model: The suspect model
            test_images: List of test image paths (unmarked)
            threshold: Detection threshold
            
        Returns:
            Tuple of (is_poisoned, confidence_score)
        """
        model.to(self.device)
        model.eval()
        
        # Extract features from test images
        preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        feature_correlations = []
        
        with torch.no_grad():
            for img_path in test_images:
                img = Image.open(img_path).convert('RGB')
                img_tensor = preprocess(img).unsqueeze(0).to(self.device)
                
                # Extract features
                features = model(img_tensor)
                features = features.view(features.size(0), -1).cpu().numpy()
                
                # Compute correlation with signature
                signature_truncated = self.signature[:features.shape[1]]
                correlation = np.dot(features.squeeze(), signature_truncated)
                feature_correlations.append(correlation)
        
        # Average correlation score
        avg_correlation = np.mean(feature_correlations)
        is_poisoned = avg_correlation > threshold

        return bool(is_poisoned), float(avg_correlation)


if __name__ == "__main__":
    # Example usage
    print("Radioactive Data Poison - Core Implementation")
    print("=" * 50)
    
    # Initialize marker
    marker = RadioactiveMarker(epsilon=0.01, device='cpu')
    
    # Generate unique signature
    signature = marker.generate_signature()
    print(f"Generated signature with {len(signature)} dimensions")
    
    # Save signature
    marker.save_signature("signature.json")
    print("Signature saved to signature.json")
    
    print("\nReady to poison images!")
    print("Use the CLI wrapper: python poison_cli.py")
