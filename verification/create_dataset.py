#!/usr/bin/env python3
"""
Create a verification dataset for testing radioactive poisoning detection.

This script:
1. Downloads or generates clean images
2. Poisons a subset of them
3. Organizes them into clean/ and poisoned/ folders
4. Ready for verify_poison.py to train a model and detect poisoning
"""

import os
import sys
from pathlib import Path
from PIL import Image
import numpy as np

# Add poison-core to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'poison-core'))
from radioactive_poison import RadioactiveMarker


def generate_synthetic_image(size=(224, 224)):
    """Generate a random synthetic image for testing."""
    # Create random RGB image
    img_array = np.random.randint(0, 256, (*size, 3), dtype=np.uint8)
    return Image.fromarray(img_array, 'RGB')


def generate_pattern_image(size=(224, 224), pattern_type='checkerboard'):
    """Generate patterned images for better visual verification."""
    img = Image.new('RGB', size)
    pixels = img.load()

    for i in range(size[0]):
        for j in range(size[1]):
            if pattern_type == 'checkerboard':
                # Checkerboard pattern
                if (i // 32 + j // 32) % 2 == 0:
                    pixels[i, j] = (255, 255, 255)
                else:
                    pixels[i, j] = (50, 50, 50)
            elif pattern_type == 'gradient':
                # Horizontal gradient
                color_value = int((i / size[0]) * 255)
                pixels[i, j] = (color_value, 128, 255 - color_value)
            elif pattern_type == 'stripes':
                # Vertical stripes
                if (i // 16) % 2 == 0:
                    pixels[i, j] = (100, 200, 255)
                else:
                    pixels[i, j] = (255, 100, 150)

    return img


def create_verification_dataset(
    output_dir='verification_data',
    num_clean=20,
    num_poisoned=20,
    epsilon=0.01,
    pgd_steps=5,
    use_patterns=True
):
    """
    Create a verification dataset with clean and poisoned images.

    Args:
        output_dir: Output directory for dataset
        num_clean: Number of clean images
        num_poisoned: Number of poisoned images
        epsilon: Poisoning strength
        pgd_steps: PGD iterations (1=FGSM, 5-10=robust)
        use_patterns: Use patterned images instead of random noise
    """
    output_path = Path(output_dir)
    clean_dir = output_path / 'clean'
    poisoned_dir = output_path / 'poisoned'

    # Create directories
    clean_dir.mkdir(parents=True, exist_ok=True)
    poisoned_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("🔬 Creating Verification Dataset")
    print("=" * 60)
    print(f"Output directory: {output_path}")
    print(f"Clean images: {num_clean}")
    print(f"Poisoned images: {num_poisoned}")
    print(f"Epsilon: {epsilon}")
    print(f"PGD steps: {pgd_steps}")
    print(f"Pattern mode: {use_patterns}")
    print()

    # Generate clean images
    print("1. Generating clean images...")
    patterns = ['checkerboard', 'gradient', 'stripes', 'random']

    for i in range(num_clean):
        if use_patterns:
            pattern = patterns[i % len(patterns)]
            if pattern == 'random':
                img = generate_synthetic_image()
            else:
                img = generate_pattern_image(pattern_type=pattern)
        else:
            img = generate_synthetic_image()

        img_path = clean_dir / f'clean_{i:03d}.jpg'
        img.save(img_path, quality=95)

        if (i + 1) % 5 == 0:
            print(f"  Created {i + 1}/{num_clean} clean images")

    print(f"✅ Created {num_clean} clean images\n")

    # Generate poisoned images
    print("2. Generating and poisoning images...")

    # Initialize marker with single signature
    marker = RadioactiveMarker(epsilon=epsilon, device='cpu')
    marker.generate_signature()

    # Save signature
    signature_path = output_path / 'signature.json'
    marker.save_signature(str(signature_path))
    print(f"  Generated signature: {signature_path}")

    # Create poisoned images
    temp_dir = output_path / 'temp'
    temp_dir.mkdir(exist_ok=True)

    for i in range(num_poisoned):
        # Generate clean image
        if use_patterns:
            pattern = patterns[i % len(patterns)]
            if pattern == 'random':
                img = generate_synthetic_image()
            else:
                img = generate_pattern_image(pattern_type=pattern)
        else:
            img = generate_synthetic_image()

        # Save temporarily
        temp_clean = temp_dir / f'temp_{i}.jpg'
        img.save(temp_clean, quality=95)

        # Poison it
        poisoned_path = poisoned_dir / f'poisoned_{i:03d}.jpg'
        marker.poison_image(
            str(temp_clean),
            str(poisoned_path),
            pgd_steps=pgd_steps
        )

        # Clean up temp
        temp_clean.unlink()

        if (i + 1) % 5 == 0:
            print(f"  Poisoned {i + 1}/{num_poisoned} images")

    # Clean up temp directory
    temp_dir.rmdir()

    print(f"✅ Created {num_poisoned} poisoned images\n")

    # Summary
    print("=" * 60)
    print("✅ Dataset Creation Complete!")
    print("=" * 60)
    print(f"\nDataset structure:")
    print(f"  {output_path}/")
    print(f"    ├── clean/        ({num_clean} images)")
    print(f"    ├── poisoned/     ({num_poisoned} images)")
    print(f"    └── signature.json")
    print()
    print("Next steps:")
    print(f"  1. Verify dataset: ls -R {output_path}")
    print(f"  2. Run verification: python verification/verify_poison.py --data {output_path} --signature {signature_path} --epochs 5")
    print()
    print("Expected outcome:")
    print("  - Model trained on poisoned data should show HIGH signature correlation")
    print("  - Clean model (no poisoned data) should show LOW correlation")
    print("=" * 60)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Create verification dataset')
    parser.add_argument('--output', default='verification_data', help='Output directory')
    parser.add_argument('--clean', type=int, default=20, help='Number of clean images')
    parser.add_argument('--poisoned', type=int, default=20, help='Number of poisoned images')
    parser.add_argument('--epsilon', type=float, default=0.01, help='Poisoning strength')
    parser.add_argument('--pgd-steps', type=int, default=5, help='PGD iterations')
    parser.add_argument('--random', action='store_true', help='Use random noise instead of patterns')

    args = parser.parse_args()

    create_verification_dataset(
        output_dir=args.output,
        num_clean=args.clean,
        num_poisoned=args.poisoned,
        epsilon=args.epsilon,
        pgd_steps=args.pgd_steps,
        use_patterns=not args.random
    )
