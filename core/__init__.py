"""
Sigil Core - Compression-Robust Perceptual Hash Tracking

This module provides the primary functionality for extracting, comparing,
and storing perceptual hashes from video content.
"""

from .perceptual_hash import (
    load_video_frames,
    extract_perceptual_features,
    compute_perceptual_hash,
    hamming_distance
)

__version__ = "1.0.0"
__all__ = [
    "load_video_frames",
    "extract_perceptual_features",
    "compute_perceptual_hash",
    "hamming_distance"
]
