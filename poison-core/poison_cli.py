#!/usr/bin/env python3
"""
Basilisk Poison CLI - Simple command-line interface for image poisoning

Usage:
    python poison_cli.py poison input.jpg output.jpg
    python poison_cli.py batch input_folder/ output_folder/
    python poison_cli.py detect model.pth signature.json test_images/
"""

import click
import os
from pathlib import Path
import json
from radioactive_poison import RadioactiveMarker, RadioactiveDetector
from tqdm import tqdm
import torch


@click.group()
def cli():
    """Basilisk - Protect your creative work from AI training."""
    pass


@cli.command()
@click.argument('input_image', type=click.Path(exists=True))
@click.argument('output_image', type=click.Path())
@click.option('--epsilon', default=0.01, help='Perturbation strength (0.005-0.05)')
@click.option('--pgd-steps', default=1, help='PGD iterations (1=FGSM, 5-10=robust PGD)')
@click.option('--signature', default=None, type=click.Path(), help='Use existing signature file')
@click.option('--device', default='cpu', type=click.Choice(['cpu', 'cuda']), help='Device to use')
def poison(input_image, output_image, epsilon, pgd_steps, signature, device):
    """
    Poison a single image.
    
    Example:
        python poison_cli.py poison my_art.jpg my_art_poisoned.jpg
    """
    click.echo(f"🐍 Basilisk - Poisoning {input_image}")
    click.echo(f"   Epsilon: {epsilon}")
    click.echo(f"   PGD Steps: {pgd_steps} {'(FGSM - fast)' if pgd_steps == 1 else '(PGD - robust)'}")

    # Initialize marker
    marker = RadioactiveMarker(epsilon=epsilon, device=device)
    
    # Load or generate signature
    if signature:
        click.echo(f"   Loading signature from {signature}")
        marker.load_signature(signature)
        signature_path = signature
    else:
        click.echo("   Generating new signature...")
        marker.generate_signature()
        signature_path = output_image.replace('.jpg', '_signature.json').replace('.png', '_signature.json')
        marker.save_signature(signature_path)
        click.echo(f"   Signature saved to {signature_path}")
    
    # Poison the image
    try:
        output_path, metadata = marker.poison_image(input_image, output_image, pgd_steps=pgd_steps)
        click.echo(f"✅ Poisoned image saved to {output_path}")
        click.echo(f"   Signature ID: {metadata['signature_id']}")
        
        # Save metadata
        metadata_path = output_image.replace('.jpg', '_metadata.json').replace('.png', '_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        click.echo(f"   Metadata saved to {metadata_path}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise


@cli.command()
@click.argument('input_folder', type=click.Path(exists=True))
@click.argument('output_folder', type=click.Path())
@click.option('--epsilon', default=0.01, help='Perturbation strength')
@click.option('--device', default='cpu', type=click.Choice(['cpu', 'cuda']))
def batch(input_folder, output_folder, epsilon, device):
    """
    Poison all images in a folder.
    
    Example:
        python poison_cli.py batch ./my_art/ ./poisoned_art/
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all images
    image_extensions = {'.jpg', '.jpeg', '.png'}
    images = [f for f in input_path.iterdir() 
              if f.suffix.lower() in image_extensions]
    
    if not images:
        click.echo("❌ No images found in input folder")
        return
    
    click.echo(f"🐍 Basilisk - Batch poisoning {len(images)} images")
    
    # Initialize marker with single signature for all images
    marker = RadioactiveMarker(epsilon=epsilon, device=device)
    marker.generate_signature()
    
    # Save signature
    signature_path = output_path / "batch_signature.json"
    marker.save_signature(str(signature_path))
    click.echo(f"   Signature saved to {signature_path}")
    
    # Poison all images
    successful = 0
    failed = 0
    
    for img_path in tqdm(images, desc="Poisoning"):
        try:
            output_img = output_path / img_path.name
            marker.poison_image(str(img_path), str(output_img))
            successful += 1
        except Exception as e:
            click.echo(f"   Failed on {img_path.name}: {e}", err=True)
            failed += 1
    
    click.echo(f"\n✅ Complete: {successful} successful, {failed} failed")


@cli.command()
@click.argument('model_path', type=click.Path(exists=True))
@click.argument('signature_path', type=click.Path(exists=True))
@click.argument('test_images_folder', type=click.Path(exists=True))
@click.option('--threshold', default=0.1, help='Detection threshold')
def detect(model_path, signature_path, test_images_folder, threshold):
    """
    Detect if a model was trained on poisoned data.
    
    Example:
        python poison_cli.py detect trained_model.pth signature.json test_images/
    """
    click.echo(f"🔍 Basilisk - Detecting radioactive signature")
    click.echo(f"   Model: {model_path}")
    click.echo(f"   Signature: {signature_path}")
    
    # Load model
    model = torch.load(model_path)
    
    # Find test images
    test_path = Path(test_images_folder)
    image_extensions = {'.jpg', '.jpeg', '.png'}
    test_images = [str(f) for f in test_path.iterdir() 
                   if f.suffix.lower() in image_extensions]
    
    if not test_images:
        click.echo("❌ No test images found")
        return
    
    click.echo(f"   Using {len(test_images)} test images")
    
    # Run detection
    detector = RadioactiveDetector(signature_path)
    is_poisoned, confidence = detector.detect(model, test_images, threshold)
    
    click.echo(f"\n{'🎯' if is_poisoned else '❌'} Detection Result:")
    click.echo(f"   Poisoned: {is_poisoned}")
    click.echo(f"   Confidence: {confidence:.4f}")
    click.echo(f"   Threshold: {threshold}")
    
    if is_poisoned:
        click.echo(f"\n⚠️  This model appears to have been trained on your poisoned data!")


@cli.command()
def info():
    """Display information about Basilisk."""
    click.echo("""
🐍 Project Basilisk - AI Data Poisoning Platform

Protect your creative work from unauthorized AI training using
radioactive data marking.

Commands:
  poison   - Poison a single image
  batch    - Poison multiple images in a folder
  detect   - Detect if a model was trained on poisoned data
  info     - Show this information

How it works:
  1. Generate a unique cryptographic signature
  2. Inject imperceptible perturbations that encode this signature
  3. The signature persists through model training
  4. Detect the signature in trained models to prove theft

Phase 1: Images ✓
Phase 2: Video (coming soon)
Phase 3: Code, Audio, Text (coming soon)

Visit: https://github.com/abendrothj/basilisk
    """)


if __name__ == '__main__':
    cli()
