import os
import sys
import numpy as np
import subprocess
from perceptual_hash import load_video_frames, extract_perceptual_features, compute_perceptual_hash, hamming_distance

def test_video(video_path, max_frames=None, crf=28):
    compressed_path = video_path + f".crf{crf}.mp4"
    # Step 1: Load original video and compute hash
    frames_orig = load_video_frames(video_path, max_frames)
    features_orig = extract_perceptual_features(frames_orig)
    hash_orig = compute_perceptual_hash(features_orig)
    # Step 2: Compress video
    cmd = [
        'ffmpeg', '-y', '-i', video_path,
        '-c:v', 'libx264', '-preset', 'medium', '-crf', str(crf),
        '-an', compressed_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Compression failed for {video_path}: {result.stderr.decode()}")
        return None
    # Step 3: Load compressed video and compute hash
    frames_comp = load_video_frames(compressed_path, max_frames)
    features_comp = extract_perceptual_features(frames_comp)
    hash_comp = compute_perceptual_hash(features_comp)
    # Step 4: Compare hashes
    dist = hamming_distance(hash_orig, hash_comp)
    # Cleanup
    os.remove(compressed_path)
    return dist, len(hash_orig)

def batch_test_videos(directory, max_frames=None, crf=28):
    results = []
    for fname in os.listdir(directory):
        if not fname.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            continue
        video_path = os.path.join(directory, fname)
        print(f"Testing {fname}...")
        res = test_video(video_path, max_frames, crf)
        if res is not None:
            dist, hash_len = res
            print(f"  Hamming distance: {dist} / {hash_len}")
            results.append((fname, dist, hash_len))
        else:
            print(f"  FAILED: {fname}")
    print("\nSummary:")
    for fname, dist, hash_len in results:
        print(f"{fname}: {dist} / {hash_len}")
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python batch_hash_robustness.py <video_dir> [max_frames] [crf]")
        sys.exit(1)
    video_dir = sys.argv[1]
    max_frames = int(sys.argv[2]) if len(sys.argv) > 2 else None
    crf = int(sys.argv[3]) if len(sys.argv) > 3 else 28
    batch_test_videos(video_dir, max_frames, crf)
