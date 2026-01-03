#!/usr/bin/env python3
"""
Manage Sigil signing identities

Usage:
    python -m cli.identity show              # Show current identity
    python -m cli.identity generate          # Generate new identity
    python -m cli.identity export            # Export public key
    python -m cli.identity import KEY_FILE   # Import existing key

Example:
    python -m cli.identity show
    python -m cli.identity generate --overwrite
    python -m cli.identity export --output pubkey.pem
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.crypto_signatures import SigilIdentity


def cmd_show(args):
    """Show current identity information"""
    try:
        identity = SigilIdentity()

        if not identity.private_key:
            print("❌ No identity found")
            print()
            print(f"📁 Expected location: {identity.private_key_path}")
            print()
            print(f"💡 Generate a new identity with:")
            print(f"   python -m cli.identity generate")
            sys.exit(1)

        print("✅ Sigil Identity Found")
        print()
        print(f"🔐 Key ID: {identity.key_id}")
        print(f"📁 Private key: {identity.private_key_path}")
        print(f"📄 Public key:  {identity.public_key_path}")
        print(f"🔑 Algorithm: Ed25519")
        print()

        if args.verbose:
            print(f"📋 Public Key (PEM format):")
            print(identity.export_public_key())
            print()
            print(f"⚠️  Security Notice:")
            print(f"   Your private key is stored unencrypted (like SSH keys).")
            print(f"   Keep it safe, but if compromised, just generate a new one.")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_generate(args):
    """Generate new identity"""
    try:
        identity = SigilIdentity()

        # Check if identity already exists
        if identity.private_key_path.exists() and not args.overwrite:
            print(f"❌ Identity already exists at: {identity.private_key_path}")
            print()
            print(f"🔐 Current Key ID: {identity.key_id}")
            print()
            print(f"💡 To replace it, use:")
            print(f"   python -m cli.identity generate --overwrite")
            print()
            print(f"⚠️  Warning: Overwriting will invalidate all existing signatures!")
            sys.exit(1)

        # Generate new keypair
        print("🔐 Generating new Ed25519 identity...")
        priv_path, pub_path = identity.generate(overwrite=args.overwrite)

        print()
        print("✅ Identity Created Successfully")
        print()
        print(f"🔐 Key ID: {identity.key_id}")
        print(f"📁 Private key: {priv_path}")
        print(f"📄 Public key:  {pub_path}")
        print()
        print(f"💡 Next steps:")
        print(f"   1. Sign a video hash: python -m cli.extract video.mp4 --sign")
        print(f"   2. Verify signature:  python -m cli.verify video.mp4.signature.json")
        print(f"   3. Export public key: python -m cli.identity export")
        print()
        print(f"⚠️  Security Notice:")
        print(f"   Your private key is stored unencrypted at {priv_path}")
        print(f"   This is intentional (like SSH keys) for ease of use.")
        print(f"   If compromised, generate a new identity and re-sign your content.")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_export(args):
    """Export public key"""
    try:
        identity = SigilIdentity()

        if not identity.private_key:
            print(f"❌ No identity found. Generate one first:", file=sys.stderr)
            print(f"   python -m cli.identity generate", file=sys.stderr)
            sys.exit(1)

        public_key_pem = identity.export_public_key()

        if args.output:
            output_path = Path(args.output)
            output_path.write_text(public_key_pem)
            print(f"✅ Public key exported to: {output_path}")
            print(f"🔐 Key ID: {identity.key_id}")
        else:
            print(public_key_pem)

        if args.verbose and not args.output:
            print(f"\n🔐 Key ID: {identity.key_id}", file=sys.stderr)
            print(f"💡 Share this public key to allow others to verify your signatures", file=sys.stderr)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_import(args):
    """Import existing private key"""
    try:
        import_path = Path(args.key_file)
        if not import_path.exists():
            print(f"❌ Key file not found: {import_path}", file=sys.stderr)
            sys.exit(1)

        identity = SigilIdentity()

        # Check if identity already exists
        if identity.private_key_path.exists() and not args.overwrite:
            print(f"❌ Identity already exists at: {identity.private_key_path}")
            print()
            print(f"💡 To replace it, use:")
            print(f"   python -m cli.identity import {import_path} --overwrite")
            sys.exit(1)

        # Copy key file to default location
        import shutil
        identity._ensure_key_directory()
        shutil.copy(import_path, identity.private_key_path)
        identity.private_key_path.chmod(0o600)

        # Load and verify
        identity._load_keys()

        print("✅ Identity Imported Successfully")
        print()
        print(f"🔐 Key ID: {identity.key_id}")
        print(f"📁 Imported to: {identity.private_key_path}")
        print()
        print(f"💡 You can now sign videos with this identity:")
        print(f"   python -m cli.extract video.mp4 --sign")

    except Exception as e:
        print(f"Error importing key: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Manage Sigil signing identities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  show        Show current identity information
  generate    Generate new Ed25519 keypair
  export      Export public key for sharing
  import      Import existing private key

Examples:
  python -m cli.identity show
  python -m cli.identity generate
  python -m cli.identity export --output pubkey.pem
  python -m cli.identity import /path/to/key.pem
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Show command
    parser_show = subparsers.add_parser('show', help='Show current identity')
    parser_show.add_argument('--verbose', action='store_true', help='Show full public key')
    parser_show.set_defaults(func=cmd_show)

    # Generate command
    parser_gen = subparsers.add_parser('generate', help='Generate new identity')
    parser_gen.add_argument('--overwrite', action='store_true', help='Overwrite existing identity')
    parser_gen.set_defaults(func=cmd_generate)

    # Export command
    parser_export = subparsers.add_parser('export', help='Export public key')
    parser_export.add_argument('--output', type=str, help='Output file path (default: stdout)')
    parser_export.add_argument('--verbose', action='store_true', help='Show additional info')
    parser_export.set_defaults(func=cmd_export)

    # Import command
    parser_import = subparsers.add_parser('import', help='Import existing private key')
    parser_import.add_argument('key_file', type=str, help='Path to private key file')
    parser_import.add_argument('--overwrite', action='store_true', help='Overwrite existing identity')
    parser_import.set_defaults(func=cmd_import)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    args.func(args)


if __name__ == "__main__":
    main()
