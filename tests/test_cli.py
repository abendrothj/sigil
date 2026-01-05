#!/usr/bin/env python3
"""
Comprehensive tests for all CLI commands

Tests cover:
- cli.extract: Video hash extraction with various options
- cli.identity: Identity management (generate, show, export, import)
- cli.compare: Hash comparison with videos and hash files
- cli.verify: Signature verification
- cli.anchor: Signature anchoring to web platforms
"""

import pytest
import subprocess
import sys
import json
import tempfile
import shutil
from pathlib import Path
import cv2
import numpy as np

# Test video creation helper
@pytest.fixture
def test_video():
    """Create a test video file"""
    temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
    temp_path = temp_file.name
    temp_file.close()

    # Create simple test video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_path, fourcc, 30.0, (224, 224))

    for i in range(30):
        frame = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        out.write(frame)

    out.release()

    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


def run_cli(module, args):
    """Run a CLI module and return result"""
    cmd = [sys.executable, '-m', f'cli.{module}'] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result


class TestCLIExtract:
    """Test cli.extract command"""

    def test_extract_basic(self, test_video):
        """Test basic hash extraction"""
        result = run_cli('extract', [test_video])

        assert result.returncode == 0
        hash_output = result.stdout.strip()
        assert len(hash_output) == 256
        assert all(c in '01' for c in hash_output)

    def test_extract_hex_format(self, test_video):
        """Test hash extraction in hex format"""
        result = run_cli('extract', [test_video, '--format', 'hex'])

        assert result.returncode == 0
        hash_output = result.stdout.strip()
        assert len(hash_output) == 64
        assert all(c in '0123456789abcdef' for c in hash_output)

    def test_extract_to_file(self, test_video, temp_dir):
        """Test hash extraction to file"""
        output_file = temp_dir / 'hash.txt'
        result = run_cli('extract', [test_video, '--output', str(output_file)])

        assert result.returncode == 0
        assert output_file.exists()

        hash_content = output_file.read_text().strip()
        assert len(hash_content) == 256
        assert all(c in '01' for c in hash_content)

    def test_extract_with_custom_seed(self, test_video):
        """Test hash extraction with custom seed"""
        result1 = run_cli('extract', [test_video, '--seed', '42'])
        result2 = run_cli('extract', [test_video, '--seed', 'custom_seed'])

        assert result1.returncode == 0
        assert result2.returncode == 0

        hash1 = result1.stdout.strip()
        hash2 = result2.stdout.strip()

        # Different seeds should produce different hashes
        assert hash1 != hash2

    def test_extract_custom_frames(self, test_video):
        """Test hash extraction with custom frame count"""
        result = run_cli('extract', [test_video, '--frames', '15'])

        assert result.returncode == 0
        hash_output = result.stdout.strip()
        assert len(hash_output) == 256

    def test_extract_nonexistent_file(self):
        """Test hash extraction with nonexistent file"""
        result = run_cli('extract', ['/nonexistent/video.mp4'])

        assert result.returncode == 1
        assert 'not found' in result.stderr.lower()

    def test_extract_verbose(self, test_video):
        """Test verbose output"""
        result = run_cli('extract', [test_video, '--verbose'])

        assert result.returncode == 0
        assert 'Loading video' in result.stdout
        assert 'Hash Statistics' in result.stdout


class TestCLIIdentity:
    """Test cli.identity command"""

    def test_identity_generate(self, temp_dir, monkeypatch):
        """Test identity generation"""
        # Mock the default key directory
        monkeypatch.setenv('HOME', str(temp_dir))
        key_dir = temp_dir / '.sigil'
        key_dir.mkdir(parents=True, exist_ok=True)

        # Set XDG_CONFIG_HOME to use temp directory
        monkeypatch.setenv('XDG_CONFIG_HOME', str(temp_dir))

        result = run_cli('identity', ['generate'])

        assert result.returncode == 0
        assert 'Identity Created' in result.stdout
        assert 'Key ID' in result.stdout

    def test_identity_show_no_identity(self, temp_dir, monkeypatch):
        """Test showing identity when none exists"""
        monkeypatch.setenv('HOME', str(temp_dir))
        monkeypatch.setenv('XDG_CONFIG_HOME', str(temp_dir))

        result = run_cli('identity', ['show'])

        assert result.returncode == 1
        assert 'No identity found' in result.stdout

    def test_identity_export(self, temp_dir, monkeypatch):
        """Test exporting public key"""
        monkeypatch.setenv('HOME', str(temp_dir))
        monkeypatch.setenv('XDG_CONFIG_HOME', str(temp_dir))

        # First generate an identity
        run_cli('identity', ['generate'])

        # Then export it
        result = run_cli('identity', ['export'])

        assert result.returncode == 0
        assert '-----BEGIN PUBLIC KEY-----' in result.stdout
        assert '-----END PUBLIC KEY-----' in result.stdout


class TestCLICompare:
    """Test cli.compare command"""

    def test_compare_hash_files(self, temp_dir):
        """Test comparing two hash files"""
        # Create two identical hash files
        hash_str = '0' * 128 + '1' * 128

        hash_file1 = temp_dir / 'hash1.txt'
        hash_file2 = temp_dir / 'hash2.txt'

        hash_file1.write_text(hash_str)
        hash_file2.write_text(hash_str)

        result = run_cli('compare', [
            str(hash_file1),
            str(hash_file2),
            '--hash-input'
        ])

        assert result.returncode == 0
        assert 'Hamming Distance: 0' in result.stdout
        assert 'Match: ✅ YES' in result.stdout

    def test_compare_different_hashes(self, temp_dir):
        """Test comparing different hashes"""
        hash1 = '0' * 256
        hash2 = '1' * 256

        hash_file1 = temp_dir / 'hash1.txt'
        hash_file2 = temp_dir / 'hash2.txt'

        hash_file1.write_text(hash1)
        hash_file2.write_text(hash2)

        result = run_cli('compare', [
            str(hash_file1),
            str(hash_file2),
            '--hash-input'
        ])

        # Should not match (256 bits different)
        assert result.returncode == 1
        assert 'Hamming Distance: 256' in result.stdout
        assert 'Match: ❌ NO' in result.stdout

    def test_compare_hex_hashes(self, temp_dir):
        """Test comparing hex format hashes"""
        # Create hex format hashes
        hash_hex1 = 'a' * 64
        hash_hex2 = 'a' * 64

        hash_file1 = temp_dir / 'hash1.txt'
        hash_file2 = temp_dir / 'hash2.txt'

        hash_file1.write_text(hash_hex1)
        hash_file2.write_text(hash_hex2)

        result = run_cli('compare', [
            str(hash_file1),
            str(hash_file2),
            '--hash-input'
        ])

        assert result.returncode == 0
        assert 'Hamming Distance: 0' in result.stdout

    def test_compare_with_threshold(self, temp_dir):
        """Test comparison with custom threshold"""
        # Create slightly different hashes (10 bits different)
        hash1 = '0' * 246 + '1' * 10
        hash2 = '0' * 256

        hash_file1 = temp_dir / 'hash1.txt'
        hash_file2 = temp_dir / 'hash2.txt'

        hash_file1.write_text(hash1)
        hash_file2.write_text(hash2)

        # Should match with threshold of 15
        result = run_cli('compare', [
            str(hash_file1),
            str(hash_file2),
            '--hash-input',
            '--threshold', '15'
        ])

        assert result.returncode == 0
        assert 'Match: ✅ YES' in result.stdout


class TestCLIVerify:
    """Test cli.verify command"""

    def test_verify_valid_signature(self, temp_dir, monkeypatch):
        """Test verifying a valid signature"""
        monkeypatch.setenv('HOME', str(temp_dir))
        monkeypatch.setenv('XDG_CONFIG_HOME', str(temp_dir))

        # Import crypto modules
        from core.crypto_signatures import SigilIdentity, SignatureManager

        # Create identity
        identity = SigilIdentity(key_dir=str(temp_dir))
        identity.generate_keys()

        # Create signature
        sig_manager = SignatureManager(identity)
        sig_file = temp_dir / 'test.signature.json'

        test_hash = 'a' * 64
        sig_manager.create_signature_file(
            hash_hex=test_hash,
            output_path=sig_file,
            video_filename='test.mp4'
        )

        # Verify signature
        result = run_cli('verify', [str(sig_file)])

        assert result.returncode == 0
        assert 'SIGNATURE VALID' in result.stdout
        assert 'Key ID' in result.stdout

    def test_verify_tampered_signature(self, temp_dir, monkeypatch):
        """Test verifying a tampered signature"""
        monkeypatch.setenv('HOME', str(temp_dir))
        monkeypatch.setenv('XDG_CONFIG_HOME', str(temp_dir))

        from core.crypto_signatures import SigilIdentity, SignatureManager

        # Create identity and signature
        identity = SigilIdentity(key_dir=str(temp_dir))
        identity.generate_keys()

        sig_manager = SignatureManager(identity)
        sig_file = temp_dir / 'test.signature.json'

        test_hash = 'a' * 64
        sig_manager.create_signature_file(
            hash_hex=test_hash,
            output_path=sig_file
        )

        # Tamper with signature
        with sig_file.open('r') as f:
            sig_doc = json.load(f)

        sig_doc['claim']['hash_hex'] = 'b' * 64

        with sig_file.open('w') as f:
            json.dump(sig_doc, f)

        # Verify should fail
        result = run_cli('verify', [str(sig_file)])

        assert result.returncode == 1
        assert 'SIGNATURE INVALID' in result.stdout

    def test_verify_json_output(self, temp_dir, monkeypatch):
        """Test JSON output format"""
        monkeypatch.setenv('HOME', str(temp_dir))
        monkeypatch.setenv('XDG_CONFIG_HOME', str(temp_dir))

        from core.crypto_signatures import SigilIdentity, SignatureManager

        identity = SigilIdentity(key_dir=str(temp_dir))
        identity.generate_keys()

        sig_manager = SignatureManager(identity)
        sig_file = temp_dir / 'test.signature.json'

        sig_manager.create_signature_file(
            hash_hex='a' * 64,
            output_path=sig_file
        )

        result = run_cli('verify', [str(sig_file), '--json'])

        assert result.returncode == 0

        output = json.loads(result.stdout)
        assert output['valid'] is True
        assert 'key_id' in output
        assert 'hash_hex' in output

    def test_verify_nonexistent_file(self):
        """Test verifying nonexistent file"""
        result = run_cli('verify', ['/nonexistent/signature.json'])

        assert result.returncode == 1
        assert 'not found' in result.stderr.lower()


class TestCLIAnchor:
    """Test cli.anchor command"""

    def test_anchor_twitter(self, temp_dir, monkeypatch):
        """Test anchoring to Twitter"""
        monkeypatch.setenv('HOME', str(temp_dir))
        monkeypatch.setenv('XDG_CONFIG_HOME', str(temp_dir))

        from core.crypto_signatures import SigilIdentity, SignatureManager

        # Create signature
        identity = SigilIdentity(key_dir=str(temp_dir))
        identity.generate_keys()

        sig_manager = SignatureManager(identity)
        sig_file = temp_dir / 'test.signature.json'

        sig_manager.create_signature_file(
            hash_hex='a' * 64,
            output_path=sig_file
        )

        # Anchor to Twitter
        tweet_url = 'https://twitter.com/user/status/123456789'
        result = run_cli('anchor', [
            str(sig_file),
            '--twitter', tweet_url
        ])

        assert result.returncode == 0
        assert 'anchored successfully' in result.stdout

        # Verify anchor was added
        with sig_file.open('r') as f:
            sig_doc = json.load(f)

        assert 'anchors' in sig_doc
        assert len(sig_doc['anchors']) == 1
        assert sig_doc['anchors'][0]['type'] == 'twitter'
        assert sig_doc['anchors'][0]['url'] == tweet_url

    def test_anchor_github(self, temp_dir, monkeypatch):
        """Test anchoring to GitHub"""
        monkeypatch.setenv('HOME', str(temp_dir))
        monkeypatch.setenv('XDG_CONFIG_HOME', str(temp_dir))

        from core.crypto_signatures import SigilIdentity, SignatureManager

        identity = SigilIdentity(key_dir=str(temp_dir))
        identity.generate_keys()

        sig_manager = SignatureManager(identity)
        sig_file = temp_dir / 'test.signature.json'

        sig_manager.create_signature_file(
            hash_hex='a' * 64,
            output_path=sig_file
        )

        # Anchor to GitHub
        github_url = 'https://github.com/user/repo/issues/123'
        result = run_cli('anchor', [
            str(sig_file),
            '--github', github_url
        ])

        assert result.returncode == 0

        # Verify anchor was added
        with sig_file.open('r') as f:
            sig_doc = json.load(f)

        assert sig_doc['anchors'][0]['type'] == 'github'

    def test_anchor_list(self, temp_dir, monkeypatch):
        """Test listing anchors"""
        monkeypatch.setenv('HOME', str(temp_dir))
        monkeypatch.setenv('XDG_CONFIG_HOME', str(temp_dir))

        from core.crypto_signatures import SigilIdentity, SignatureManager

        identity = SigilIdentity(key_dir=str(temp_dir))
        identity.generate_keys()

        sig_manager = SignatureManager(identity)
        sig_file = temp_dir / 'test.signature.json'

        sig_manager.create_signature_file(
            hash_hex='a' * 64,
            output_path=sig_file
        )

        # Add multiple anchors
        run_cli('anchor', [
            str(sig_file),
            '--twitter', 'https://twitter.com/user/status/123'
        ])

        run_cli('anchor', [
            str(sig_file),
            '--github', 'https://github.com/user/repo/issues/1'
        ])

        # List anchors
        result = run_cli('anchor', [str(sig_file), '--list'])

        assert result.returncode == 0
        assert 'Timestamp Anchors (2)' in result.stdout
        assert 'Twitter' in result.stdout
        assert 'Github' in result.stdout

    def test_anchor_duplicate_prevention(self, temp_dir, monkeypatch):
        """Test that duplicate URLs are not added"""
        monkeypatch.setenv('HOME', str(temp_dir))
        monkeypatch.setenv('XDG_CONFIG_HOME', str(temp_dir))

        from core.crypto_signatures import SigilIdentity, SignatureManager

        identity = SigilIdentity(key_dir=str(temp_dir))
        identity.generate_keys()

        sig_manager = SignatureManager(identity)
        sig_file = temp_dir / 'test.signature.json'

        sig_manager.create_signature_file(
            hash_hex='a' * 64,
            output_path=sig_file
        )

        tweet_url = 'https://twitter.com/user/status/123'

        # Add anchor twice
        run_cli('anchor', [str(sig_file), '--twitter', tweet_url])
        result = run_cli('anchor', [str(sig_file), '--twitter', tweet_url])

        assert 'already anchored' in result.stdout

        # Verify only one anchor exists
        with sig_file.open('r') as f:
            sig_doc = json.load(f)

        assert len(sig_doc['anchors']) == 1

    def test_anchor_no_method_specified(self, temp_dir):
        """Test error when no anchoring method specified"""
        sig_file = temp_dir / 'test.signature.json'
        sig_file.write_text('{}')

        result = run_cli('anchor', [str(sig_file)])

        assert result.returncode == 1
        assert 'must specify' in result.stderr.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
