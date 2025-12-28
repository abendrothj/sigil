import sys
import numpy as np
import subprocess
import os

# Import the perceptual hash functions
from perceptual_hash import load_video_frames, extract_perceptual_features, compute_perceptual_hash, hamming_distance

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_hash_robustness.py <video_path> [max_frames]")
        sys.exit(1)
    video_path = sys.argv[1]
    max_frames = int(sys.argv[2]) if len(sys.argv) > 2 else None
    compressed_path = "compressed_temp.mp4"

    # Step 1: Load original video and compute hash
    frames_orig = load_video_frames(video_path, max_frames)
    features_orig = extract_perceptual_features(frames_orig)
    hash_orig = compute_perceptual_hash(features_orig)
    print(f"Original hash sum: {np.sum(hash_orig)} / {len(hash_orig)}")

    # Step 2: Compress video
    cmd = [
        'ffmpeg', '-y', '-i', video_path,
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '28',
        '-an', compressed_path
    ]
    print(f"Compressing video: {' '.join(cmd)}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print("Compression failed:", result.stderr.decode())
        sys.exit(1)

    # Step 3: Load compressed video and compute hash
    frames_comp = load_video_frames(compressed_path, max_frames)
    features_comp = extract_perceptual_features(frames_comp)
    hash_comp = compute_perceptual_hash(features_comp)
    print(f"Compressed hash sum: {np.sum(hash_comp)} / {len(hash_comp)}")

    # Step 4: Compare hashes
    dist = hamming_distance(hash_orig, hash_comp)
    print(f"Hamming distance: {dist} / {len(hash_orig)}")

    # Cleanup
    os.remove(compressed_path)

if __name__ == "__main__":
    main()
