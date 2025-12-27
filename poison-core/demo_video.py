#!/usr/bin/env python3
"""
Demo script for video poisoning
Creates a synthetic test video and poisons it
"""

import cv2
import numpy as np
from pathlib import Path
from video_poison import VideoRadioactiveMarker


def create_test_video(output_path: str, duration_seconds: int = 5, fps: int = 30):
    """
    Create a synthetic test video with moving objects.

    Args:
        output_path: Where to save the video
        duration_seconds: Length of video
        fps: Frames per second
    """
    print(f"Creating test video: {output_path}")

    width, height = 640, 480
    total_frames = duration_seconds * fps

    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for frame_idx in range(total_frames):
        # Create blank frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Add moving circle
        t = frame_idx / fps
        x = int(width / 2 + 150 * np.cos(2 * np.pi * t / 2))
        y = int(height / 2 + 100 * np.sin(2 * np.pi * t / 2))
        cv2.circle(frame, (x, y), 30, (0, 255, 0), -1)

        # Add moving square
        x2 = int(width / 2 + 100 * np.sin(2 * np.pi * t / 3))
        y2 = int(height / 2 + 100 * np.cos(2 * np.pi * t / 3))
        cv2.rectangle(frame, (x2 - 20, y2 - 20), (x2 + 20, y2 + 20), (255, 0, 0), -1)

        # Add frame number
        cv2.putText(frame, f"Frame {frame_idx}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        out.write(frame)

    out.release()
    print(f"✅ Created test video: {total_frames} frames, {fps}fps")


def demo_optical_flow_poisoning():
    """Demonstrate optical flow based video poisoning."""
    print("=" * 60)
    print("🐍 Basilisk Video Poisoning Demo")
    print("=" * 60)
    print()

    # Create test video
    test_video = "demo_input.mp4"
    create_test_video(test_video, duration_seconds=3, fps=30)
    print()

    # Initialize video marker
    print("Initializing VideoRadioactiveMarker...")
    marker = VideoRadioactiveMarker(
        epsilon=0.03,
        temporal_period=30,  # 1 second cycle at 30fps
        device='cpu'
    )

    # Generate signature
    print("Generating temporal signature...")
    signature = marker.generate_signature()
    print(f"  Temporal signature: {len(signature)} frames")
    print(f"  Signature ID: {hex(marker.seed)[:16]}")

    # Save signature
    sig_path = "demo_signature.json"
    marker.save_signature(sig_path)
    print(f"  Saved to: {sig_path}")
    print()

    # Poison video (optical flow method)
    print("Poisoning video with optical flow method...")
    poisoned_video_flow = "demo_output_flow.mp4"
    output_path, metadata = marker.poison_video(
        test_video,
        poisoned_video_flow,
        method='optical_flow'
    )
    print()
    print(f"✅ Poisoned video saved: {poisoned_video_flow}")
    print(f"   Method: optical_flow")
    print(f"   Resolution: {metadata['resolution']}")
    print(f"   Total frames: {metadata['total_frames']}")
    print()

    # Poison video (per-frame method for comparison)
    print("Poisoning video with per-frame method...")
    poisoned_video_frame = "demo_output_frame.mp4"
    output_path2, metadata2 = marker.poison_video(
        test_video,
        poisoned_video_frame,
        method='frame'
    )
    print()
    print(f"✅ Poisoned video saved: {poisoned_video_frame}")
    print(f"   Method: frame")
    print(f"   Resolution: {metadata2['resolution']}")
    print(f"   Total frames: {metadata2['total_frames']}")
    print()

    # Summary
    print("=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print()
    print("Files created:")
    print(f"  • {test_video} - Original test video")
    print(f"  • {poisoned_video_flow} - Poisoned (optical flow method)")
    print(f"  • {poisoned_video_frame} - Poisoned (per-frame method)")
    print(f"  • {sig_path} - Signature file")
    print()
    print("Compare the videos:")
    print(f"  • Original should have smooth motion")
    print(f"  • Poisoned videos should look nearly identical")
    print(f"  • Optical flow method is more robust to compression")
    print()
    print("Next steps:")
    print("  1. Compress videos with ffmpeg (various CRF levels)")
    print("  2. Test signature preservation after compression")
    print("  3. Train a video model to test detection")


if __name__ == "__main__":
    demo_optical_flow_poisoning()
