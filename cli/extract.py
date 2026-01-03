#!/usr/bin/env python3
"""
Extract perceptual hash from video file

Usage:
    python -m cli.extract VIDEO_PATH [OPTIONS]

Example:
    python -m cli.extract video.mp4 --frames 60 --output hash.txt
"""

import argparse
import sys
from pathlib import Path
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.perceptual_hash import (
    load_video_frames,
    extract_perceptual_features,
    compute_perceptual_hash
)
from core.crypto_signatures import SignatureManager


def main():
    parser = argparse.ArgumentParser(
        description="Extract compression-robust perceptual hash from video"
    )
    parser.add_argument(
        "video_path",
        type=str,
        help="Path to video file"
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=60,
        help="Number of frames to process (default: 60)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (default: print to stdout)"
    )
    parser.add_argument(
        "--format",
        choices=["binary", "hex", "decimal"],
        default="binary",
        help="Output format (default: binary)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose output"
    )
    parser.add_argument(
        "--sign",
        action="store_true",
        help="Create cryptographic signature for ownership proof"
    )
    parser.add_argument(
        "--key-path",
        type=str,
        help="Path to private key (default: ~/.sigil/identity.pem)"
    )
    parser.add_argument(
        "--signature-output",
        type=str,
        help="Output path for signature.json (default: same directory as video with .signature.json extension)"
    )

    args = parser.parse_args()

    # Validate video path
    video_path = Path(args.video_path)
    if not video_path.exists():
        print(f"Error: Video file not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    try:
        # Load video frames
        if args.verbose:
            print(f"Loading video: {video_path}")
            print(f"Processing {args.frames} frames...")

        frames = load_video_frames(str(video_path), max_frames=args.frames)

        if args.verbose:
            print(f"Loaded {len(frames)} frames")

        # Extract features
        if args.verbose:
            print("Extracting perceptual features (Canny edges, Gabor textures, Laplacian saliency, RGB histograms)...")

        features = extract_perceptual_features(frames)

        # Compute hash
        if args.verbose:
            print("Computing 256-bit perceptual hash...")

        hash_binary = compute_perceptual_hash(features)

        # Format output
        if args.format == "binary":
            hash_str = ''.join(map(str, hash_binary.astype(int)))
        elif args.format == "hex":
            hash_str = hex(int(''.join(map(str, hash_binary.astype(int))), 2))[2:].zfill(64)
        elif args.format == "decimal":
            hash_str = str(int(''.join(map(str, hash_binary.astype(int))), 2))

        # Output
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(hash_str + '\n')
            if args.verbose:
                print(f"\n✅ Hash saved to: {output_path}")
        else:
            print(hash_str)

        # Print stats if verbose
        if args.verbose:
            print(f"\n📊 Hash Statistics:")
            print(f"   Length: {len(hash_binary)} bits")
            print(f"   Bits set: {np.sum(hash_binary)} / 256")
            print(f"   Format: {args.format}")

        # Create cryptographic signature if requested
        if args.sign:
            if args.verbose:
                print("\n🔐 Creating cryptographic signature...")

            # Convert hash to hex format for signing
            hash_hex = hex(int(''.join(map(str, hash_binary.astype(int))), 2))[2:].zfill(64)

            # Initialize signature manager
            sig_manager = SignatureManager()
            if args.key_path:
                from core.crypto_signatures import SigilIdentity
                sig_manager.identity = SigilIdentity(Path(args.key_path))

            # Determine signature output path
            if args.signature_output:
                sig_output_path = Path(args.signature_output)
            else:
                sig_output_path = video_path.with_suffix(video_path.suffix + '.signature.json')

            # Create metadata
            metadata = {
                "video_filename": video_path.name,
                "frames_analyzed": len(frames),
                "hash_format": args.format
            }

            # Generate and save signature
            sig_file = sig_manager.create_signature_file(
                hash_hex=hash_hex,
                output_path=sig_output_path,
                video_filename=video_path.name,
                additional_metadata=metadata
            )

            if args.verbose:
                print(f"✅ Signature saved to: {sig_file}")
                print(f"   Key ID: {sig_manager.identity.key_id}")
                print(f"   Algorithm: Ed25519")
                print(f"\n💡 Next steps:")
                print(f"   1. Verify signature: python -m cli.verify {sig_file}")
                print(f"   2. Post to Twitter/GitHub for timestamp proof")
                print(f"   3. Anchor: python -m cli.anchor {sig_file} --twitter <tweet_url>")
            else:
                print(f"\n✅ Signature: {sig_file}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
