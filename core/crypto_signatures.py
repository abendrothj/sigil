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
import base64
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

# Assuming this import is intended based on the diff, despite the partial line.
# If this is incorrect, please clarify.
from .perceptual_hash import compute_match_score


class SigilIdentity:
    """
    Manages cryptographic identity and signing for Sigil.
    Uses Ed25519 for signing (fast, secure, small signatures).
    """
    
    DEFAULT_KEY_DIR = Path.home() / ".sigil" / "keys"
    DEFAULT_PRIVATE_KEY = "id_ed25519"
    DEFAULT_PUBLIC_KEY = "id_ed25519.pub"

    def __init__(self, key_dir: str | None = None, private_key_name: str | None = None):
        """
        Initialize Sigil Identity.
        
        Args:
            key_dir: Directory to store keys (default: ~/.sigil/keys)
            private_key_name: Name of private key file (default: id_ed25519)
        """
        if key_dir:
            self.key_dir = Path(key_dir)
        else:
            self.key_dir = self.DEFAULT_KEY_DIR
            
        params_private = private_key_name or self.DEFAULT_PRIVATE_KEY
        params_public = f"{params_private}.pub"
        
        self.private_key_path = self.key_dir / params_private
        self.public_key_path = self.key_dir / params_public
        
        self.private_key: ed25519.Ed25519PrivateKey | None = None
        self.public_key: ed25519.Ed25519PublicKey | None = None
        
        # Load keys if they exist
        if self.private_key_path.exists():
            self.load_keys()

    def generate_keys(self, force: bool = False) -> tuple[str, str]:
        """
        Generate a new Ed25519 key pair.
        
        Args:
            force: Overwrite existing keys if True
            
        Returns:
            Tuple of (private_key_path, public_key_path)
        """
        if self.private_key_path.exists() and not force:
            raise FileExistsError(f"Key already exists at {self.private_key_path}")
            
        self.key_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate private key
        self.private_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
        
        # Save private key
        private_bytes = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.OpenSSH,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        with open(self.private_key_path, "wb") as f:
            f.write(private_bytes)
        
        # Set permissions to 600 (read/write only by owner)
        os.chmod(self.private_key_path, 0o600)
            
        # Save public key
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH
        )
        
        with open(self.public_key_path, "wb") as f:
            f.write(public_bytes)
            
        return str(self.private_key_path), str(self.public_key_path)

    def load_keys(self):
        """Load keys from disk"""
        if not self.private_key_path.exists():
            raise FileNotFoundError(f"No private key found at {self.private_key_path}")
            
        with open(self.private_key_path, "rb") as f:
            private_bytes = f.read()
            
        self.private_key = serialization.load_ssh_private_key(
            private_bytes,
            password=None
        )
        
        # Derive public key
        if isinstance(self.private_key, ed25519.Ed25519PrivateKey):
            self.public_key = self.private_key.public_key()
        else:
             raise ValueError("Key is not an Ed25519 key")

    def get_public_key_string(self) -> str:
        """Get public key as OpenSSH string"""
        if not self.public_key:
            raise ValueError("Keys not loaded")
            
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH
        )
        return public_bytes.decode('utf-8').strip()

    def get_key_id(self) -> str:
        """Get key fingerprint (SHA256 of public key blob)"""
        if not self.public_key:
            raise ValueError("Keys not loaded")
            
        # Get raw bytes for fingerprinting (ignoring OpenSSH header)
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        return hashlib.sha256(public_bytes).hexdigest()

    def sign_hash(self, hash_hex: str, metadata: dict[str, str | dict] | None = None) -> dict[str, str | dict]:
        """
        Cryptographically sign a perceptual hash.
        
        Args:
            hash_hex: Hex string of the perceptual hash
            metadata: Optional dictionary of metadata to include in signature
            
        Returns:
            Dictionary containing signature, public key, and signed data
        """
        if not self.private_key:
            raise ValueError("Private key not loaded")
            
        # Create canonical payload to sign
        # We sign: hash + metadata + timestamp
        claim: dict[str, str | dict] = {
            "hash_hex": hash_hex,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
        
        # Canonical JSON for signing (sorted keys, no whitespace)
        payload_bytes = json.dumps(claim, sort_keys=True, separators=(',', ':')).encode('utf-8')
        
        # Sign payload
        signature_bytes = self.private_key.sign(payload_bytes)
        signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')
        
        return {
            "claim": claim,
            "signature": signature_b64,
            "public_key": self.get_public_key_string(),
            "key_id": self.get_key_id(),
            "algorithm": "Ed25519",
            "version": "1.0"
        }

    @staticmethod
    def verify_signature(signature_doc: dict[str, str | dict]) -> tuple[bool, str | None]:
        """
        Verify a Sigil signature.
        
        Args:
            signature_doc: Dictionary returned by sign_hash
            
        Returns:
            (is_valid, error_message)
        """
        try:
            claim = signature_doc.get("claim")
            signature_b64 = str(signature_doc.get("signature"))
            public_key_str = str(signature_doc.get("public_key"))
            
            if not claim or not signature_b64 or not public_key_str:
                return False, "Missing required fields"
                
            # Parse public key
            # OpenSSH format: "ssh-ed25519 <base64> <comment>"
            parts = public_key_str.split()
            if len(parts) < 2:
                return False, "Invalid public key format"
                
            key_type = parts[0]
            if key_type != "ssh-ed25519":
                return False, f"Unsupported key type: {key_type}"
                
            public_key_bytes = base64.b64decode(parts[1])
            public_key = serialization.load_ssh_public_key(
                f"{key_type} {parts[1]}".encode('utf-8')
            )
            
            if not isinstance(public_key, ed25519.Ed25519PublicKey):
                return False, "Not an Ed25519 key"
                
            # Reconstruct payload
            payload_bytes = json.dumps(claim, sort_keys=True, separators=(',', ':')).encode('utf-8')
            signature_bytes = base64.b64decode(signature_b64)
            
            # Verify
            public_key.verify(signature_bytes, payload_bytes)
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

        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return public_bytes.decode('ascii')


class SignatureManager:
    """
    High-level API for creating and managing signature files.
    """

    def __init__(self, identity: SigilIdentity | None = None):
        """
        Initialize signature manager.

        Args:
            identity: SigilIdentity instance (default: use ~/.sigil/keys)
        """
        self.identity = identity or SigilIdentity()

    def create_signature_file(
        self,
        hash_hex: str,
        output_path: Path,
        video_filename: str | None = None,
        additional_metadata: dict[str, Any] | None = None
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
        if not self.identity.private_key:
            print("[Sigil] Generating new Ed25519 identity...")
            priv, pub = self.identity.generate_keys()
            print(f"[Sigil] ✓ Identity created: {self.identity.get_key_id()}")
            print(f"[Sigil]   Private key: {priv}")
            print(f"[Sigil]   Public key:  {pub}")

        # Build metadata
        metadata: dict[str, Any] = additional_metadata or {}
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
    def verify_signature_file(signature_path: Path) -> tuple[bool, dict[str, Any]]:
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
                "key_id": signature_doc.get("key_id"), # flat structure in new sign_hash
                "hash_hex": signature_doc.get("claim", {}).get("hash_hex"),
                "signed_at": signature_doc.get("claim", {}).get("timestamp"),
                "algorithm": signature_doc.get("algorithm"),
                "anchors": signature_doc.get("anchors", []),
                "error": error
            }

            return is_valid, info

        except Exception as e:
            return False, {"error": f"Failed to load signature file: {str(e)}"}


# Convenience functions for CLI usage

def create_identity(key_dir: str | None = None, overwrite: bool = False) -> str:
    """Create new Sigil identity. Returns key_id."""
    identity = SigilIdentity(key_dir=key_dir)
    identity.generate_keys(force=overwrite)
    return identity.get_key_id()


def sign_hash(hash_hex: str, metadata: dict[str, Any] | None = None, key_dir: str | None = None) -> dict[str, Any]:
    """Sign a hash with the default or specified identity."""
    identity = SigilIdentity(key_dir=key_dir)
    if not identity.private_key:
         identity.generate_keys()
    return identity.sign_hash(hash_hex, metadata)


def verify_signature(signature_doc: dict[str, Any]) -> tuple[bool, str | None]:
    """Verify a signature document. Returns (is_valid, error_message)."""
    return SigilIdentity.verify_signature(signature_doc)


def get_key_id(key_dir: str | None = None) -> str:
    """Get the key ID of the current identity."""
    identity = SigilIdentity(key_dir=key_dir)
    if not identity.private_key:
        raise ValueError("No identity found. Generate one with create_identity() first.")
    return identity.get_key_id()
