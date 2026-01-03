#!/usr/bin/env python3
"""
Verify Sigil cryptographic signature

Usage:
    python -m cli.verify SIGNATURE_FILE [OPTIONS]

Example:
    python -m cli.verify video.mp4.signature.json --verbose
"""

import argparse
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.crypto_signatures import SignatureManager, SigilIdentity


def main():
    parser = argparse.ArgumentParser(
        description="Verify Sigil cryptographic signature for video hash ownership proof"
    )
    parser.add_argument(
        "signature_file",
        type=str,
        help="Path to signature.json file"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose output"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    # Validate signature file path
    sig_path = Path(args.signature_file)
    if not sig_path.exists():
        print(f"Error: Signature file not found: {sig_path}", file=sys.stderr)
        sys.exit(1)

    try:
        # Verify signature
        is_valid, info = SignatureManager.verify_signature_file(sig_path)

        # JSON output mode
        if args.json:
            output = {
                "valid": is_valid,
                "signature_file": str(sig_path),
                **info
            }
            print(json.dumps(output, indent=2))
            sys.exit(0 if is_valid else 1)

        # Human-readable output
        if is_valid:
            print("✅ SIGNATURE VALID")
            print()
            print(f"📄 File: {sig_path.name}")
            print(f"🔐 Key ID: {info.get('key_id', 'Unknown')}")
            print(f"🔑 Algorithm: {info.get('algorithm', 'Ed25519')}")
            print(f"📊 Hash: {info.get('hash_hex', 'Unknown')[:16]}...{info.get('hash_hex', '')[-16:]}")
            print(f"📅 Signed At: {info.get('signed_at', 'Unknown')}")

            # Show anchors if present
            anchors = info.get('anchors', [])
            if anchors:
                print(f"\n🔗 Web2 Timestamp Anchors:")
                for anchor in anchors:
                    anchor_type = anchor.get('type', 'unknown').capitalize()
                    anchor_url = anchor.get('url', 'No URL')
                    print(f"   - {anchor_type}: {anchor_url}")
            else:
                if args.verbose:
                    print(f"\n💡 No timestamp anchors found.")
                    print(f"   Consider posting this signature to Twitter/GitHub for timestamp proof:")
                    print(f"   python -m cli.anchor {sig_path} --twitter <tweet_url>")

            if args.verbose:
                print(f"\n🔬 Verification Details:")
                print(f"   This signature mathematically proves that the signer possessed")
                print(f"   the private key corresponding to {info.get('key_id', 'Unknown')}")
                print(f"   at the time of signing ({info.get('signed_at', 'Unknown')}).")
                print(f"   The perceptual hash is bound to this signature.")

            sys.exit(0)

        else:
            print("❌ SIGNATURE INVALID")
            print()
            print(f"📄 File: {sig_path.name}")
            print(f"⚠️  Error: {info.get('error', 'Unknown verification error')}")

            if args.verbose:
                print(f"\n🔬 Possible Reasons:")
                print(f"   - Signature file has been tampered with")
                print(f"   - Hash value has been modified")
                print(f"   - Signature was created with a different key")
                print(f"   - File format is corrupted or invalid")

            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
