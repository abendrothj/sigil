#!/usr/bin/env python3
"""
Basilisk Video Poison CLI - Command-line interface for video poisoning

Usage:
    python video_poison_cli.py poison input.mp4 output.mp4
    python video_poison_cli.py poison input.mp4 output.mp4 --method optical_flow
    python video_poison_cli.py batch input_folder/ output_folder/
"""

import click
import os
from pathlib import Path
import json
from video_poison import VideoRadioactiveMarker, VideoRadioactiveDetector
from tqdm import tqdm


@click.group()
def cli():
    """Basilisk Video - Protect your videos from AI training (Sora Defense)."""
    pass


@cli.command()
@click.argument('input_video', type=click.Path(exists=True))
@click.argument('output_video', type=click.Path())
@click.option('--epsilon', default=0.02, help='Perturbation strength (0.01-0.05)')
@click.option('--temporal-period', default=30, help='Frames per signature cycle')
@click.option('--method', default='optical_flow', type=click.Choice(['optical_flow', 'frame']),
              help='Poisoning method: optical_flow (motion) or frame (per-frame)')
@click.option('--signature', default=None, type=click.Path(), help='Use existing signature file')
@click.option('--device', default='cpu', type=click.Choice(['cpu', 'cuda']), help='Device to use')
def poison(input_video, output_video, epsilon, temporal_period, method, signature, device):
    """
    Poison a single video.

    Example:
        python video_poison_cli.py poison my_video.mp4 protected.mp4
        python video_poison_cli.py poison my_video.mp4 protected.mp4 --method optical_flow
    """
    click.echo(f"🐍 Basilisk Video - Poisoning {input_video}")
    click.echo(f"   Method: {method}")
    click.echo(f"   Epsilon: {epsilon}")
    click.echo(f"   Temporal Period: {temporal_period} frames")

    # Initialize marker
    marker = VideoRadioactiveMarker(
        epsilon=epsilon,
        temporal_period=temporal_period,
        device=device
    )

    # Load or generate signature
    if signature:
        click.echo(f"   Loading signature from {signature}")
        marker.load_signature(signature)
        signature_path = signature
    else:
        click.echo("   Generating new signature...")
        marker.generate_signature()
        signature_path = output_video.replace('.mp4', '_signature.json')
        marker.save_signature(signature_path)
        click.echo(f"   Signature saved to {signature_path}")

    # Poison the video
    try:
        click.echo("")
        output_path, metadata = marker.poison_video(
            input_video,
            output_video,
            method=method
        )

        click.echo(f"\n✅ Poisoned video saved to {output_path}")
        click.echo(f"   Signature ID: {metadata['signature_id']}")
        click.echo(f"   Resolution: {metadata['resolution']}")
        click.echo(f"   FPS: {metadata['fps']}")
        click.echo(f"   Total Frames: {metadata['total_frames']}")

        # Save metadata
        metadata_path = output_video.replace('.mp4', '_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        click.echo(f"   Metadata saved to {metadata_path}")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise


@cli.command()
@click.argument('input_folder', type=click.Path(exists=True))
@click.argument('output_folder', type=click.Path())
@click.option('--epsilon', default=0.02, help='Perturbation strength')
@click.option('--temporal-period', default=30, help='Frames per signature cycle')
@click.option('--method', default='optical_flow', type=click.Choice(['optical_flow', 'frame']))
@click.option('--device', default='cpu', type=click.Choice(['cpu', 'cuda']))
def batch(input_folder, output_folder, epsilon, temporal_period, method, device):
    """
    Poison all videos in a folder.

    Example:
        python video_poison_cli.py batch ./my_videos/ ./poisoned_videos/
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    # Find all videos
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
    videos = [f for f in input_path.iterdir()
              if f.suffix.lower() in video_extensions]

    if not videos:
        click.echo("❌ No videos found in input folder")
        return

    click.echo(f"🐍 Basilisk Video - Batch poisoning {len(videos)} videos")
    click.echo(f"   Method: {method}")

    # Initialize marker with single signature for all videos
    marker = VideoRadioactiveMarker(
        epsilon=epsilon,
        temporal_period=temporal_period,
        device=device
    )
    marker.generate_signature()

    # Save signature
    signature_path = output_path / "batch_video_signature.json"
    marker.save_signature(str(signature_path))
    click.echo(f"   Signature saved to {signature_path}")

    # Poison all videos
    successful = 0
    failed = 0

    click.echo("")
    for video_path in videos:
        try:
            click.echo(f"Processing {video_path.name}...")
            output_video = output_path / video_path.name
            marker.poison_video(str(video_path), str(output_video), method=method)
            successful += 1
            click.echo("")
        except Exception as e:
            click.echo(f"   Failed on {video_path.name}: {e}", err=True)
            failed += 1
            click.echo("")

    click.echo(f"\n✅ Complete: {successful} successful, {failed} failed")


@cli.command()
def info():
    """Display information about Basilisk Video."""
    click.echo("""
🐍 Basilisk Video - AI Video Poisoning (Phase 2)

Protect your videos from unauthorized AI training (OpenAI Sora, Meta Make-A-Video, etc.)

Methods:
  optical_flow - Poison motion vectors between frames (RECOMMENDED)
                 Robust to compression, survives H.264/AV1 encoding

  frame        - Poison each frame as an image
                 Simpler but less robust to video compression

How it works:
  1. Extract optical flow (motion) between frames
  2. Inject temporal signature into motion vectors
  3. Reconstruct frames with poisoned motion
  4. Small perturbations create "impossible physics"
  5. AI models learn these patterns
  6. Signature survives compression and frame drops

Commands:
  poison   - Poison a single video
  batch    - Poison multiple videos in a folder
  info     - Show this information

Example:
  # Protect a single video
  python video_poison_cli.py poison my_video.mp4 protected.mp4

  # Protect all videos in a folder
  python video_poison_cli.py batch ./videos/ ./protected/

  # Use custom settings
  python video_poison_cli.py poison input.mp4 output.mp4 \\
    --epsilon 0.03 \\
    --temporal-period 60 \\
    --method optical_flow

Why Optical Flow?
  - Video codecs compress motion separately from pixels
  - Motion vectors preserved even with heavy compression
  - Creates imperceptible "motion watermark"
  - Much more robust than per-frame poisoning

Recommended Settings:
  --epsilon 0.02-0.03 (higher than images due to compression)
  --temporal-period 30 (1 second at 30fps)
  --method optical_flow (default, most robust)

Phase 2 Status: BETA
- ✅ Optical flow poisoning implemented
- ✅ Per-frame poisoning implemented
- ⚠️  Detection algorithm in progress
- ⚠️  Compression robustness testing needed

Visit: https://github.com/abendrothj/basilisk
    """)


if __name__ == '__main__':
    cli()
