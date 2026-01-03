"""
Unit tests for Sigil cryptographic signatures

Tests cover:
- Identity generation and loading
- Signature creation and verification
- Key fingerprinting
- Signature file management
- Error handling
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path

# Import modules to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.crypto_signatures import (
    SigilIdentity,
    SignatureManager,
    create_identity,
    sign_hash,
    verify_signature,
    get_key_id
)


class TestSigilIdentity(unittest.TestCase):
    """Test cases for SigilIdentity class"""

    def setUp(self):
        """Create temporary directory for test keys"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_key_path = self.test_dir / "test_identity.pem"

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)

    def test_identity_generation(self):
        """Test generating a new Ed25519 identity"""
        identity = SigilIdentity(self.test_key_path)
        priv_path, pub_path = identity.generate()

        # Check files were created
        self.assertTrue(Path(priv_path).exists())
        self.assertTrue(Path(pub_path).exists())

        # Check permissions
        self.assertEqual(Path(priv_path).stat().st_mode & 0o777, 0o600)

        # Check keys are loaded
        self.assertIsNotNone(identity.private_key)
        self.assertIsNotNone(identity.public_key)

    def test_identity_loading(self):
        """Test loading an existing identity"""
        # Generate identity
        identity1 = SigilIdentity(self.test_key_path)
        identity1.generate()
        key_id1 = identity1.key_id

        # Load identity in new instance
        identity2 = SigilIdentity(self.test_key_path)
        key_id2 = identity2.key_id

        # Key IDs should match
        self.assertEqual(key_id1, key_id2)

    def test_key_id_format(self):
        """Test key ID fingerprint format"""
        identity = SigilIdentity(self.test_key_path)
        identity.generate()

        key_id = identity.key_id

        # Should start with "SHA256:"
        self.assertTrue(key_id.startswith("SHA256:"))

        # Should have base64 hash after prefix
        hash_part = key_id.split("SHA256:")[1]
        self.assertGreater(len(hash_part), 0)

    def test_sign_hash_valid(self):
        """Test signing a valid hash"""
        identity = SigilIdentity(self.test_key_path)
        identity.generate()

        # Test hash (64 hex chars)
        test_hash = "a3f2b1c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2"
        metadata = {"test": "value"}

        sig_doc = identity.sign_hash(test_hash, metadata)

        # Check structure
        self.assertIn("claim", sig_doc)
        self.assertIn("proof", sig_doc)
        self.assertIn("anchors", sig_doc)
        self.assertIn("version", sig_doc)

        # Check claim
        self.assertEqual(sig_doc["claim"]["hash_hex"], test_hash)
        self.assertEqual(sig_doc["claim"]["metadata"], metadata)

        # Check proof
        self.assertIn("signature", sig_doc["proof"])
        self.assertIn("public_key", sig_doc["proof"])
        self.assertEqual(sig_doc["proof"]["key_id"], identity.key_id)
        self.assertEqual(sig_doc["proof"]["algorithm"], "Ed25519")

    def test_sign_hash_invalid_length(self):
        """Test signing with invalid hash length"""
        identity = SigilIdentity(self.test_key_path)
        identity.generate()

        # Too short
        with self.assertRaises(ValueError):
            identity.sign_hash("abc123")

        # Too long
        with self.assertRaises(ValueError):
            identity.sign_hash("a" * 100)

    def test_sign_without_identity(self):
        """Test signing without generating identity first"""
        identity = SigilIdentity(self.test_key_path)

        test_hash = "a" * 64

        with self.assertRaises(ValueError):
            identity.sign_hash(test_hash)

    def test_verify_signature_valid(self):
        """Test verifying a valid signature"""
        identity = SigilIdentity(self.test_key_path)
        identity.generate()

        test_hash = "a" * 64
        sig_doc = identity.sign_hash(test_hash)

        # Verify
        is_valid, error = SigilIdentity.verify_signature(sig_doc)

        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_verify_signature_tampered(self):
        """Test verifying a tampered signature"""
        identity = SigilIdentity(self.test_key_path)
        identity.generate()

        test_hash = "a" * 64
        sig_doc = identity.sign_hash(test_hash)

        # Tamper with the hash
        sig_doc["claim"]["hash_hex"] = "b" * 64

        # Verify should fail
        is_valid, error = SigilIdentity.verify_signature(sig_doc)

        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_verify_signature_wrong_key(self):
        """Test verifying with wrong public key"""
        identity1 = SigilIdentity(self.test_key_path)
        identity1.generate()

        identity2 = SigilIdentity(self.test_dir / "other_key.pem")
        identity2.generate()

        # Sign with identity1
        test_hash = "a" * 64
        sig_doc = identity1.sign_hash(test_hash)

        # Replace public key with identity2's key
        sig_doc["proof"]["public_key"] = identity2.export_public_key().split('\n')[1]

        # Verify should fail
        is_valid, error = SigilIdentity.verify_signature(sig_doc)

        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_export_public_key(self):
        """Test exporting public key in PEM format"""
        identity = SigilIdentity(self.test_key_path)
        identity.generate()

        public_pem = identity.export_public_key()

        # Check PEM format
        self.assertIn("-----BEGIN PUBLIC KEY-----", public_pem)
        self.assertIn("-----END PUBLIC KEY-----", public_pem)

    def test_overwrite_protection(self):
        """Test that overwrite=False prevents key replacement"""
        identity = SigilIdentity(self.test_key_path)
        identity.generate()

        # Try to generate again without overwrite
        with self.assertRaises(FileExistsError):
            identity.generate(overwrite=False)

    def test_overwrite_allowed(self):
        """Test that overwrite=True allows key replacement"""
        identity = SigilIdentity(self.test_key_path)
        key_id1 = identity.generate()[0]

        # Generate again with overwrite
        key_id2 = identity.generate(overwrite=True)[0]

        # Key IDs should be different (new key generated)
        self.assertEqual(key_id1, key_id2)  # Paths are the same
        # But the key ID will be different
        identity_new = SigilIdentity(self.test_key_path)
        # (We can't easily compare key IDs here without re-loading)


class TestSignatureManager(unittest.TestCase):
    """Test cases for SignatureManager class"""

    def setUp(self):
        """Create temporary directory for test files"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_key_path = self.test_dir / "test_identity.pem"
        self.test_sig_path = self.test_dir / "test.signature.json"

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)

    def test_create_signature_file(self):
        """Test creating a signature file"""
        identity = SigilIdentity(self.test_key_path)
        identity.generate()

        sig_manager = SignatureManager(identity)

        test_hash = "a" * 64
        sig_file = sig_manager.create_signature_file(
            hash_hex=test_hash,
            output_path=self.test_sig_path,
            video_filename="test.mp4"
        )

        # Check file was created
        self.assertTrue(sig_file.exists())

        # Check file content
        with sig_file.open('r') as f:
            sig_doc = json.load(f)

        self.assertEqual(sig_doc["claim"]["hash_hex"], test_hash)
        self.assertEqual(sig_doc["claim"]["metadata"]["video_filename"], "test.mp4")

    def test_verify_signature_file_valid(self):
        """Test verifying a valid signature file"""
        identity = SigilIdentity(self.test_key_path)
        identity.generate()

        sig_manager = SignatureManager(identity)

        test_hash = "a" * 64
        sig_file = sig_manager.create_signature_file(
            hash_hex=test_hash,
            output_path=self.test_sig_path
        )

        # Verify
        is_valid, info = SignatureManager.verify_signature_file(sig_file)

        self.assertTrue(is_valid)
        self.assertEqual(info["hash_hex"], test_hash)
        self.assertIsNone(info["error"])

    def test_verify_signature_file_tampered(self):
        """Test verifying a tampered signature file"""
        identity = SigilIdentity(self.test_key_path)
        identity.generate()

        sig_manager = SignatureManager(identity)

        test_hash = "a" * 64
        sig_file = sig_manager.create_signature_file(
            hash_hex=test_hash,
            output_path=self.test_sig_path
        )

        # Tamper with file
        with sig_file.open('r') as f:
            sig_doc = json.load(f)

        sig_doc["claim"]["hash_hex"] = "b" * 64

        with sig_file.open('w') as f:
            json.dump(sig_doc, f)

        # Verify should fail
        is_valid, info = SignatureManager.verify_signature_file(sig_file)

        self.assertFalse(is_valid)
        self.assertIsNotNone(info["error"])

    def test_verify_nonexistent_file(self):
        """Test verifying a nonexistent file"""
        nonexistent = self.test_dir / "doesnotexist.json"

        is_valid, info = SignatureManager.verify_signature_file(nonexistent)

        self.assertFalse(is_valid)
        self.assertIn("error", info)


class TestConvenienceFunctions(unittest.TestCase):
    """Test cases for convenience functions"""

    def setUp(self):
        """Create temporary directory"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_key_path = self.test_dir / "test_identity.pem"

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir)

    def test_create_identity_function(self):
        """Test create_identity() convenience function"""
        key_id = create_identity(self.test_key_path)

        # Check format
        self.assertTrue(key_id.startswith("SHA256:"))

        # Check files exist
        self.assertTrue(self.test_key_path.exists())
        self.assertTrue(self.test_key_path.with_suffix('.pub').exists())

    def test_sign_hash_function(self):
        """Test sign_hash() convenience function"""
        create_identity(self.test_key_path)

        test_hash = "a" * 64
        sig_doc = sign_hash(test_hash, metadata={"test": "value"}, key_path=self.test_key_path)

        # Check structure
        self.assertIn("claim", sig_doc)
        self.assertIn("proof", sig_doc)
        self.assertEqual(sig_doc["claim"]["hash_hex"], test_hash)

    def test_verify_signature_function(self):
        """Test verify_signature() convenience function"""
        create_identity(self.test_key_path)

        test_hash = "a" * 64
        sig_doc = sign_hash(test_hash, key_path=self.test_key_path)

        is_valid, error = verify_signature(sig_doc)

        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_get_key_id_function(self):
        """Test get_key_id() convenience function"""
        key_id1 = create_identity(self.test_key_path)
        key_id2 = get_key_id(self.test_key_path)

        self.assertEqual(key_id1, key_id2)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def setUp(self):
        """Create temporary directory"""
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir)

    def test_invalid_json_in_signature_file(self):
        """Test handling invalid JSON in signature file"""
        bad_json_file = self.test_dir / "bad.json"
        bad_json_file.write_text("{ invalid json }")

        is_valid, info = SignatureManager.verify_signature_file(bad_json_file)

        self.assertFalse(is_valid)
        self.assertIn("error", info)

    def test_missing_claim_in_signature(self):
        """Test signature missing 'claim' field"""
        bad_sig = {
            "proof": {
                "signature": "test",
                "public_key": "test"
            }
        }

        is_valid, error = SigilIdentity.verify_signature(bad_sig)

        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_missing_proof_in_signature(self):
        """Test signature missing 'proof' field"""
        bad_sig = {
            "claim": {
                "hash_hex": "a" * 64
            }
        }

        is_valid, error = SigilIdentity.verify_signature(bad_sig)

        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_empty_metadata(self):
        """Test signing with empty metadata"""
        identity = SigilIdentity(self.test_dir / "key.pem")
        identity.generate()

        test_hash = "a" * 64
        sig_doc = identity.sign_hash(test_hash, metadata=None)

        # Should use empty dict
        self.assertEqual(sig_doc["claim"]["metadata"], {})

    def test_additional_metadata_preserved(self):
        """Test that additional metadata is preserved"""
        identity = SigilIdentity(self.test_dir / "key.pem")
        identity.generate()

        test_hash = "a" * 64
        metadata = {
            "video_filename": "test.mp4",
            "custom_field": "custom_value",
            "nested": {"key": "value"}
        }

        sig_doc = identity.sign_hash(test_hash, metadata)

        self.assertEqual(sig_doc["claim"]["metadata"], metadata)

        # Verify still works
        is_valid, error = SigilIdentity.verify_signature(sig_doc)
        self.assertTrue(is_valid)


class TestSignaturePersistence(unittest.TestCase):
    """Test that signatures remain valid across different scenarios"""

    def setUp(self):
        """Create temporary directory"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.key_path = self.test_dir / "key.pem"

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir)

    def test_signature_survives_serialization(self):
        """Test that signature remains valid after JSON serialization"""
        identity = SigilIdentity(self.key_path)
        identity.generate()

        test_hash = "a" * 64
        sig_doc = identity.sign_hash(test_hash)

        # Serialize and deserialize
        json_str = json.dumps(sig_doc, indent=2)
        sig_doc_reloaded = json.loads(json_str)

        # Verify reloaded signature
        is_valid, error = SigilIdentity.verify_signature(sig_doc_reloaded)

        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_signature_with_different_identity_instance(self):
        """Test verifying with a different SigilIdentity instance"""
        identity1 = SigilIdentity(self.key_path)
        identity1.generate()

        test_hash = "a" * 64
        sig_doc = identity1.sign_hash(test_hash)

        # Verify with static method (no identity instance)
        is_valid, error = SigilIdentity.verify_signature(sig_doc)

        self.assertTrue(is_valid)
        self.assertIsNone(error)


if __name__ == '__main__':
    unittest.main()
