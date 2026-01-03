
# Perceptual Hash for Video Robustness (Sigil Project)
# ------------------------------------------------------
# Extracts robust, compression-resistant features from video frames and computes a perceptual hash.
# Designed for forensic video tracking and evidence collection.
#
# SECURITY NOTICE:
# This implementation uses a fixed seed (42) for reproducibility. This means:
# - Hashes are deterministic and publicly reproducible
# - NOT cryptographically secure - anyone can compute collisions
# - Use for forensic tracking, NOT for cryptographic proof of ownership
#
# For production security applications, consider:
# - Using a secret seed stored securely
# - Implementing hash salting per-user or per-video
# - Adding cryptographic signing on top of perceptual hash

import cv2
import numpy as np
from skimage import feature

# --- Perceptual Feature Extraction ---
def extract_perceptual_features(video_frames):
    """
    Extracts compression-robust perceptual features for each frame:
      - Edges (Canny)
      - Texture (Gabor filters)
      - Saliency (Laplacian)
      - Color histogram (32 bins/channel)
    Args:
        video_frames: list of np.ndarray (BGR)
    Returns:
        features: dict mapping frame_idx to feature dict
    """
    features = {}
    for frame_idx, frame in enumerate(video_frames):
        # 1. Edge map (Canny)
        edges = cv2.Canny(frame, 100, 200)

        # 2. Texture (Gabor filters at multiple orientations)
        textures = []
        for theta in [0, 45, 90, 135]:
            kernel = cv2.getGaborKernel((21, 21), 5, np.deg2rad(theta), 10, 0.5)
            filtered = cv2.filter2D(frame, cv2.CV_32F, kernel)
            textures.append(filtered)
        textures = np.stack(textures)

        # 3. Saliency (Laplacian)
        saliency = cv2.Laplacian(frame, cv2.CV_64F)

        # 4. Color histogram (32 bins per channel)
        hist_r = cv2.calcHist([frame], [0], None, [32], [0, 256])
        hist_g = cv2.calcHist([frame], [1], None, [32], [0, 256])
        hist_b = cv2.calcHist([frame], [2], None, [32], [0, 256])
        color_hist = np.concatenate([hist_r, hist_g, hist_b])

        features[frame_idx] = {
            'edges': edges,
            'textures': textures,
            'saliency': saliency,
            'color_hist': color_hist
        }
    return features

# --- Perceptual Hash Computation ---
def compute_perceptual_hash(features, hash_size=256):
    """
    Computes a 256-bit perceptual hash from extracted features.
    Uses random projection and incremental mean for memory efficiency.

    SECURITY WARNING: This function uses a FIXED SEED (42) for reproducibility.

    Implications:
    - Hashes are deterministic and reproducible across all installations
    - Anyone with this code can compute the same hash for any video
    - This is a FORENSIC FINGERPRINT, not a cryptographic signature
    - Attackers can precompute hash collisions if they know the seed

    Good for:
    - Tracking your own videos across platforms
    - Building forensic evidence databases
    - Detecting unauthorized reuploads

    NOT good for:
    - Cryptographic proof of ownership
    - Preventing determined adversaries from creating collisions
    - Situations where hash secrecy is required

    Args:
        features: dict of extracted features
        hash_size: output hash length (default 256)
    Returns:
        hash_bits: np.ndarray of 0/1 (length hash_size)
    """
    import time

    # WARNING: Fixed seed for reproducibility - see security warning above
    np.random.seed(42)

    first = next(iter(features.values()))
    frame_len = (
        first['edges'].size +
        first['textures'].size +
        first['saliency'].size +
        first['color_hist'].size
    )
    projection = np.random.randn(frame_len, hash_size)
    n_frames = len(features)
    projected_mean = np.zeros(hash_size)
    t_proj = 0.0
    for i, frame_features in enumerate(features.values()):
        t0 = time.time()
        frame_vec = np.concatenate([
            frame_features['edges'].flatten(),
            frame_features['textures'].flatten(),
            frame_features['saliency'].flatten(),
            frame_features['color_hist'].flatten()
        ])
        # Normalize to prevent overflow (unit vector)
        frame_vec = frame_vec / (np.linalg.norm(frame_vec) + 1e-8)
        projected = frame_vec @ projection
        projected_mean += (projected - projected_mean) / (i + 1)
        t_proj += time.time() - t0
    # Use median of all projected values for binarization
    t0 = time.time()
    median_val = np.median(projected_mean)
    hash_bits = (projected_mean > median_val).astype(int)
    t1 = time.time()
    print(f"Projection time for {n_frames} frames: {t_proj:.2f} seconds. Median/bin time: {t1-t0:.2f} seconds.")
    return hash_bits

# --- Video Loading Utility ---
def load_video_frames(path, max_frames=None):
    """
    Loads video frames from a file as a list of np.ndarray (BGR).
    Args:
        path: video file path
        max_frames: optional, limit number of frames
    Returns:
        frames: list of np.ndarray
    """
    cap = cv2.VideoCapture(path)
    frames = []
    count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
        count += 1
        if max_frames and count >= max_frames:
            break
    cap.release()
    return frames

# --- Hamming Distance ---
def hamming_distance(hash1, hash2):
    """
    Computes Hamming distance between two binary hashes.
    Args:
        hash1, hash2: np.ndarray of 0/1
    Returns:
        int: number of differing bits
    """
    return np.sum(hash1 != hash2)

if __name__ == "__main__":
    import sys
    import time
    if len(sys.argv) < 2:
        print("Usage: python perceptual_hash.py <video_path> [max_frames]")
        sys.exit(1)
    video_path = sys.argv[1]
    max_frames = int(sys.argv[2]) if len(sys.argv) > 2 else None
    t0 = time.time()
    frames = load_video_frames(video_path, max_frames)
    t1 = time.time()
    print(f"Loaded {len(frames)} frames in {t1-t0:.2f} seconds.")
    t2 = time.time()
    features = extract_perceptual_features(frames)
    t3 = time.time()
    print(f"Extracted features in {t3-t2:.2f} seconds.")
    t4 = time.time()
    hash_bits = compute_perceptual_hash(features)
    t5 = time.time()
    print(f"Computed hash in {t5-t4:.2f} seconds.")
    print(f"Perceptual hash (first 64 bits): {''.join(map(str, hash_bits[:64]))}")
    print(f"Hash sum: {np.sum(hash_bits)} / {len(hash_bits)}")
