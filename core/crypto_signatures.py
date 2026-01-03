"""
Sigil Cryptographic Signatures Module

Implements Ed25519 digital signatures for proving ownership of perceptual video hashes.
This creates a "chain of custody" for video content without relying on blockchain.

Philosophy: "PGP for Video" - Make crypto invisible unless explicitly needed.

Author: Sigil Project
License: MIT
"""

import os
import json
import hashlib
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


class SigilIdentity:
    """
    Manages Ed25519 signing identities for Sigil perceptual hashes.

    Design decisions:
    - Ed25519: Modern, fast, 32-byte keys (vs 2048-bit RSA)
    - Unencrypted storage: Like SSH keys (UX > paranoia for this threat model)
    - Auto-generation: First --sign creates identity automatically
    - Key ID: SHA256 fingerprint for human-readable identification
    """

    DEFAULT_KEY_DIR = Path.home() / ".sigil"
    DEFAULT_PRIVATE_KEY = DEFAULT_KEY_DIR / "identity.pem"
    DEFAULT_PUBLIC_KEY = DEFAULT_KEY_DIR / "identity.pub"

    def __init__(self, key_path: Optional[Path] = None):
        """
        Initialize identity manager.

        Args:
            key_path: Custom path to private key file (default: ~/.sigil/identity.pem)
        """
        self.private_key_path = Path(key_path) if key_path else self.DEFAULT_PRIVATE_KEY
        self.public_key_path = self.private_key_path.with_suffix('.pub')

        self.private_key: Optional[ed25519.Ed25519PrivateKey] = None
        self.public_key: Optional[ed25519.Ed25519PublicKey] = None

        # Load existing key or prepare for generation
        if self.private_key_path.exists():
            self._load_keys()

    def _ensure_key_directory(self):
        """Create ~/.sigil/ directory if it doesn't exist."""
        self.private_key_path.parent.mkdir(parents=True, exist_ok=True)

    def generate(self, overwrite: bool = False) -> Tuple[str, str]:
        """
        Generate new Ed25519 keypair.

        Args:
            overwrite: If True, overwrite existing keys. If False, raise error if keys exist.

        Returns:
            Tuple of (private_key_path, public_key_path)

        Raises:
            FileExistsError: If keys exist and overwrite=False
        """
        if self.private_key_path.exists() and not overwrite:
            raise FileExistsError(
                f"Identity already exists at {self.private_key_path}. "
                f"Use overwrite=True to replace, or delete the file manually."
            )

        self._ensure_key_directory()

        # Generate Ed25519 keypair
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        # Serialize private key (PEM format, unencrypted)
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()  # Unencrypted for UX
        )

        # Serialize public key (PEM format)
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # Write to disk with restricted permissions
        self.private_key_path.write_bytes(private_pem)
        self.private_key_path.chmod(0o600)  # Read/write for owner only

        self.public_key_path.write_bytes(public_pem)
        self.public_key_path.chmod(0o644)  # Read for all, write for owner

        # Load into memory
        self.private_key = private_key
        self.public_key = public_key

        return str(self.private_key_path), str(self.public_key_path)

    def _load_keys(self):
        """Load existing keys from disk."""
        # Load private key
        private_pem = self.private_key_path.read_bytes()
        self.private_key = serialization.load_pem_private_key(
            private_pem,
            password=None  # No encryption
        )

        # Derive public key from private key
        if isinstance(self.private_key, ed25519.Ed25519PrivateKey):
            self.public_key = self.private_key.public_key()
        else:
            raise ValueError(f"Invalid key type: {type(self.private_key)}. Expected Ed25519.")

    def ensure_identity(self) -> str:
        """
        Ensure identity exists, generating if necessary.
        This is called automatically on first --sign usage.

        Returns:
            Key ID (SHA256 fingerprint)
        """
        if not self.private_key:
            print(f"[Sigil] Generating new Ed25519 identity...")
            priv_path, pub_path = self.generate()
            print(f"[Sigil] ✓ Identity created: {self.key_id}")
            print(f"[Sigil]   Private key: {priv_path}")
            print(f"[Sigil]   Public key:  {pub_path}")
            print(f"[Sigil]   (Keys stored unencrypted like SSH keys)")
        return self.key_id

    @property
    def key_id(self) -> str:
        """
        Generate SHA256 fingerprint of public key (like SSH key fingerprints).
        Format: "SHA256:abc123..."
        """
        if not self.public_key:
            raise ValueError("No identity loaded. Call generate() or ensure_identity() first.")

        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )

        sha256_hash = hashlib.sha256(public_bytes).digest()
        b64_hash = base64.b64encode(sha256_hash).decode('ascii').rstrip('=')

        return f"SHA256:{b64_hash}"

    def sign_hash(
        self,
        hash_hex: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Sign a perceptual hash + metadata to prove ownership.

        Args:
            hash_hex: 64-character hex representation of 256-bit hash
            metadata: Optional metadata to include in claim (filename, timestamp, etc.)

        Returns:
            Complete signature document with claim + proof structure

        Raises:
            ValueError: If no identity loaded or invalid hash format
        """
        if not self.private_key:
            raise ValueError("No identity loaded. Call ensure_identity() first.")

        if not isinstance(hash_hex, str) or len(hash_hex) != 64:
            raise ValueError(f"Invalid hash_hex. Expected 64-char hex string, got: {hash_hex}")

        # Build claim (the data being signed)
        claim = {
            "hash_hex": hash_hex,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        # Canonical JSON for signing (sorted keys, no whitespace)
        claim_json = json.dumps(claim, sort_keys=True, separators=(',', ':'))
        claim_bytes = claim_json.encode('utf-8')

        # Sign the claim
        signature_bytes = self.private_key.sign(claim_bytes)

        # Build proof (the cryptographic evidence)
        proof = {
            "signature": base64.b64encode(signature_bytes).decode('ascii'),
            "public_key": base64.b64encode(
                self.public_key.public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw
                )
            ).decode('ascii'),
            "key_id": self.key_id,
            "algorithm": "Ed25519",
            "signed_at": claim["timestamp"]
        }

        # Return complete signature document
        return {
            "claim": claim,
            "proof": proof,
            "anchors": [],  # Populated by web2 anchoring feature
            "version": "1.0"
        }

    @staticmethod
    def verify_signature(signature_doc: Dict) -> Tuple[bool, Optional[str]]:
        """
        Verify a signature document (can be called without loading identity).

        Args:
            signature_doc: Signature document from sign_hash()

        Returns:
            Tuple of (is_valid, error_message)
            - (True, None) if signature is valid
            - (False, "error reason") if invalid
        """
        try:
            # Extract components
            claim = signature_doc.get("claim")
            proof = signature_doc.get("proof")

            if not claim or not proof:
                return False, "Missing 'claim' or 'proof' in signature document"

            # Reconstruct canonical claim JSON
            claim_json = json.dumps(claim, sort_keys=True, separators=(',', ':'))
            claim_bytes = claim_json.encode('utf-8')

            # Decode signature and public key
            signature_bytes = base64.b64decode(proof["signature"])
            public_key_bytes = base64.b64decode(proof["public_key"])

            # Reconstruct Ed25519 public key
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)

            # Verify signature
            public_key.verify(signature_bytes, claim_bytes)

            # If we reach here, signature is valid
            return True, None

        except Exception as e:
            return False, f"Verification failed: {str(e)}"

    def export_public_key(self) -> str:
        """
        Export public key in PEM format for sharing.

        Returns:
            PEM-encoded public key as string
        """
        if not self.public_key:
            raise ValueError("No identity loaded.")

        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('ascii')


class SignatureManager:
    """
    High-level API for creating and managing signature files.
    """

    def __init__(self, identity: Optional[SigilIdentity] = None):
        """
        Initialize signature manager.

        Args:
            identity: SigilIdentity instance (default: use ~/.sigil/identity.pem)
        """
        self.identity = identity or SigilIdentity()

    def create_signature_file(
        self,
        hash_hex: str,
        output_path: Path,
        video_filename: Optional[str] = None,
        additional_metadata: Optional[Dict] = None
    ) -> Path:
        """
        Create and save a signature.json file.

        Args:
            hash_hex: Perceptual hash (64-char hex)
            output_path: Where to save signature.json
            video_filename: Original video filename
            additional_metadata: Extra metadata to include

        Returns:
            Path to created signature file
        """
        # Ensure identity exists
        self.identity.ensure_identity()

        # Build metadata
        metadata = additional_metadata or {}
        if video_filename:
            metadata["video_filename"] = video_filename

        # Generate signature
        signature_doc = self.identity.sign_hash(hash_hex, metadata)

        # Write to file (pretty-printed for human readability)
        output_path = Path(output_path)
        with output_path.open('w') as f:
            json.dump(signature_doc, f, indent=2)

        return output_path

    @staticmethod
    def verify_signature_file(signature_path: Path) -> Tuple[bool, Dict]:
        """
        Verify a signature.json file.

        Args:
            signature_path: Path to signature.json

        Returns:
            Tuple of (is_valid, info_dict)
            - info_dict contains: key_id, hash_hex, signed_at, error (if any)
        """
        try:
            with signature_path.open('r') as f:
                signature_doc = json.load(f)

            is_valid, error = SigilIdentity.verify_signature(signature_doc)

            info = {
                "key_id": signature_doc.get("proof", {}).get("key_id"),
                "hash_hex": signature_doc.get("claim", {}).get("hash_hex"),
                "signed_at": signature_doc.get("proof", {}).get("signed_at"),
                "algorithm": signature_doc.get("proof", {}).get("algorithm"),
                "anchors": signature_doc.get("anchors", []),
                "error": error
            }

            return is_valid, info

        except Exception as e:
            return False, {"error": f"Failed to load signature file: {str(e)}"}


# Convenience functions for CLI usage

def create_identity(key_path: Optional[Path] = None, overwrite: bool = False) -> str:
    """Create new Sigil identity. Returns key_id."""
    identity = SigilIdentity(key_path)
    identity.generate(overwrite=overwrite)
    return identity.key_id


def sign_hash(hash_hex: str, metadata: Optional[Dict] = None, key_path: Optional[Path] = None) -> Dict:
    """Sign a hash with the default or specified identity."""
    identity = SigilIdentity(key_path)
    identity.ensure_identity()
    return identity.sign_hash(hash_hex, metadata)


def verify_signature(signature_doc: Dict) -> Tuple[bool, Optional[str]]:
    """Verify a signature document. Returns (is_valid, error_message)."""
    return SigilIdentity.verify_signature(signature_doc)


def get_key_id(key_path: Optional[Path] = None) -> str:
    """Get the key ID of the current identity."""
    identity = SigilIdentity(key_path)
    if not identity.private_key:
        raise ValueError("No identity found. Generate one with create_identity() first.")
    return identity.key_id
