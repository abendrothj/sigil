from pathlib import Path
import numpy as np
import cv2


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


def load_video_frames(video_path: str, max_frames: int | None = 60) -> list[np.ndarray]:
    """
    Load video frames from file using OpenCV.
    
    Args:
        video_path: Path to video file
        max_frames: Maximum number of frames to load (default: 60)
        
    Returns:
        List of frames as numpy arrays (RGB)
    """
    cap = cv2.VideoCapture(video_path)
    frames = []
    
    if not cap.isOpened():
        return []

    # Get total frames to sample evenly
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if max_frames:
        skip = max(1, total_frames // max_frames)
    else:
        skip = 1

    count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        if count % skip == 0:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame_rgb)
            
        count += 1
        if max_frames and len(frames) >= max_frames:
            break
            
    cap.release()
    return frames


def getGaborKernel(w: int, h: int, theta: float) -> np.ndarray:
    """Create Gabor kernel for texture extraction"""
    # Simply wrap cv2.getGaborKernel
    return cv2.getGaborKernel((w, h), 4.0, theta, 10.0, 0.5, 0, ktype=cv2.CV_32F)


def extract_perceptual_features(video_frames: list[np.ndarray]) -> dict[int, dict[str, np.ndarray]]:
    """
    Extract perceptual features from video frames.
    
    Features extracted:
    - Edges (Canny)
    - Texture (Gabor filters)
    - Saliency (Laplacian variance)
    - Color Histogram
    
    Args:
        video_frames: List of video frames
        
    Returns:
        Dictionary mapping frame index to feature dictionary
    """
    features: dict[int, dict[str, np.ndarray]] = {}
    
    # Pre-compute Gabor kernels for texture
    kernels = []
    for theta in np.arange(0, np.pi, np.pi / 4):
        kern = getGaborKernel(31, 31, theta)
        kernels.append(kern)

    for i, frame in enumerate(video_frames):
        # Resize to standard size for consistency
        frame_resized = cv2.resize(frame, (224, 224))
        gray = cv2.cvtColor(frame_resized, cv2.COLOR_RGB2GRAY)
        
        # 1. Edge detection
        edges = cv2.Canny(gray, 100, 200)
        edges_small = cv2.resize(edges, (32, 32))  # Reduce dim
        
        # 2. Texture features (Gabor)
        texture_maps = []
        for kern in kernels:
            fimg = cv2.filter2D(gray, cv2.CV_32F, kern)
            fimg = cv2.resize(fimg, (32, 32))
            texture_maps.append(fimg)
        texture_stack = np.stack(texture_maps)
        
        # 3. Saliency (simple Laplacian)
        saliency = cv2.Laplacian(gray, cv2.CV_64F).var()
        # Create a spatial map of saliency (approximation)
        saliency_map = cv2.Laplacian(gray, cv2.CV_64F)
        saliency_small = cv2.resize(saliency_map, (32, 32))

        # 4. Color Histogram (in HSV)
        hsv = cv2.cvtColor(frame_resized, cv2.COLOR_RGB2HSV)
        hist = cv2.calcHist([hsv], [0, 1, 2], None, [8, 8, 8], [0, 180, 0, 256, 0, 256])
        hist = cv2.normalize(hist, hist).flatten()

        features[i] = {
            'edges': edges_small,
            'textures': texture_stack,
            'saliency': saliency_small,
            'color_hist': hist
        }

    return features


def compute_perceptual_hash(features: dict[int, dict[str, np.ndarray]], hash_size: int = 256, seed: int | str | None = 42) -> np.ndarray:
    """
    Computes a 256-bit perceptual hash from extracted features.
    Uses random projection and incremental mean for memory efficiency.
    
    Args:
        features: Dictionary of extracted features
        hash_size: Size of hash in bits (default: 256)
        seed: Random seed for projection matrix (int, str, or None). 
              Default is 42 (fixed seed).
        
    Returns:
        Binary numpy array of hash bits (0s and 1s)
    """
    # Handle seed
    real_seed: int
    if seed is None:
        real_seed = 42
    elif isinstance(seed, int):
        real_seed = seed
    else:
        # Try to convert to int first (e.g. "42" -> 42)
        try:
            real_seed = int(seed)
        except (ValueError, TypeError):
            # Hash the string seed to get an integer
            import hashlib
            hex_digest = hashlib.sha256(str(seed).encode('utf-8')).hexdigest()
            real_seed = int(hex_digest, 16) % (2**32)  # numpy seed expects 32-bit int
        
    np.random.seed(real_seed)
    
    # Get total feature dimension
    first_features = next(iter(features.values()))
    
    dim_edges = first_features['edges'].size
    dim_textures = first_features['textures'].size
    dim_saliency = first_features['saliency'].size
    dim_color = first_features['color_hist'].size
    
    total_dim = dim_edges + dim_textures + dim_saliency + dim_color
    
    # Generate random projection matrix (LSH concept)
    # Project high-dim features to hash_size bits
    projection = np.random.randn(total_dim, hash_size)
    
    # Incremental update of projected mean
    projected_mean = np.zeros(hash_size)
    
    for i, frame_features in enumerate(features.values()):
        # Flatten and concat all features
        frame_vec = np.concatenate([
            frame_features['edges'].flatten(),
            frame_features['textures'].flatten(),
            frame_features['saliency'].flatten(),
            frame_features['color_hist'].flatten()
        ]).astype(np.float64)
        # Normalize feature vector
        frame_vec = np.nan_to_num(frame_vec, posinf=0.0, neginf=0.0)
        norm = np.linalg.norm(frame_vec)
        if norm > 1e-8:
            frame_vec = frame_vec / norm
        else:
            frame_vec = np.zeros_like(frame_vec)

        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            projected = frame_vec @ projection
        projected_mean += (projected - projected_mean) / (i + 1)
        
    # Threshold at median (common strategy for robust hashing)
    median_val = np.median(projected_mean)
    hash_bits = (projected_mean > median_val).astype(int)
    
    # t1 = time.time()
    # print(f"Projection time for {n_frames} frames: {t_proj:.2f} seconds. Median/bin time: {t1-t0:.2f} seconds.")
    
    return hash_bits


# --- Hamming Distance ---
def hamming_distance(hash1: np.ndarray, hash2: np.ndarray) -> int | np.integer:
    """
    Computes Hamming distance between two binary hashes.
    Args:
        hash1, hash2: np.ndarray of 0/1
    Returns:
        int: number of differing bits
    """
    return np.sum(hash1 != hash2)


def compute_match_score(distance: int | np.integer, threshold: int = 30) -> float:
    """
    Compute a similarity score from Hamming distance.
    
    Args:
        distance: Hamming distance
        threshold: Threshold for 0 score
        
    Returns:
        Float between 0.0 and 1.0
    """
    if distance > threshold:
        return 0.0
    # Linear interpolation: 0 distance -> 1.0, threshold distance -> 0.0
    return max(0.0, 1.0 - (float(distance) / threshold))

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
