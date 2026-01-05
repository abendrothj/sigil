#!/usr/bin/env python3
"""
Comprehensive tests for hash_database module

Tests cover:
- Database initialization and schema migration
- Hash storage and retrieval
- Similar hash queries with Hamming distance
- Platform filtering
- Statistics and metadata
- Signature storage
- Context manager usage
"""

import pytest
import tempfile
import json
from pathlib import Path
import numpy as np
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.hash_database import HashDatabase


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    temp_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_path = temp_file.name
    temp_file.close()

    db = HashDatabase(temp_path)
    yield db

    db.close()
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def sample_hash():
    """Create a sample hash for testing"""
    return np.array([1 if i % 2 == 0 else 0 for i in range(256)])


class TestHashDatabaseInit:
    """Test database initialization and schema"""

    def test_create_new_database(self):
        """Test creating a new database"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_path = temp_file.name
        temp_file.close()

        db = HashDatabase(temp_path)
        assert db.conn is not None
        assert db.db_path.exists()

        db.close()
        Path(temp_path).unlink()

    def test_schema_migration(self, temp_db):
        """Test that schema migration adds signature columns"""
        cursor = temp_db.conn.cursor()
        cursor.execute("PRAGMA table_info(hashes)")
        columns = [row[1] for row in cursor.fetchall()]

        # Check that signature columns exist
        assert 'signature' in columns
        assert 'public_key' in columns
        assert 'key_id' in columns
        assert 'signed_at' in columns
        assert 'signature_version' in columns

    def test_indexes_created(self, temp_db):
        """Test that indexes are created"""
        cursor = temp_db.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]

        assert 'idx_hash' in indexes
        assert 'idx_platform' in indexes
        assert 'idx_key_id' in indexes


class TestHashStorage:
    """Test hash storage functionality"""

    def test_store_basic_hash(self, temp_db, sample_hash):
        """Test storing a basic hash"""
        hash_id = temp_db.store_hash(sample_hash)

        assert hash_id is not None
        assert isinstance(hash_id, int)

    def test_store_hash_with_metadata(self, temp_db, sample_hash):
        """Test storing hash with full metadata"""
        metadata = {
            "resolution": "1080p",
            "duration": 120,
            "codec": "h264"
        }

        hash_id = temp_db.store_hash(
            sample_hash,
            video_id="test_video_123",
            platform="youtube",
            upload_date="2025-01-01",
            file_path="/path/to/video.mp4",
            frame_count=60,
            metadata=metadata
        )

        assert hash_id is not None

        # Verify stored data
        cursor = temp_db.conn.cursor()
        cursor.execute('SELECT video_id, platform, upload_date FROM hashes WHERE id = ?', (hash_id,))
        row = cursor.fetchone()

        assert row is not None
        assert row[0] == "test_video_123"  # video_id
        assert row[1] == "youtube"  # platform
        assert row[2] == "2025-01-01"  # upload_date

    def test_store_hash_with_signature(self, temp_db, sample_hash):
        """Test storing hash with cryptographic signature"""
        hash_id = temp_db.store_hash(
            sample_hash,
            signature="base64_signature_here",
            public_key="base64_pubkey_here",
            key_id="sha256_fingerprint",
            signed_at="2025-01-01T00:00:00Z",
            signature_version="1.0"
        )

        assert hash_id is not None

        # Verify signature data
        cursor = temp_db.conn.cursor()
        cursor.execute(
            'SELECT signature, public_key, key_id FROM hashes WHERE id = ?',
            (hash_id,)
        )
        row = cursor.fetchone()

        assert row[0] == "base64_signature_here"
        assert row[1] == "base64_pubkey_here"
        assert row[2] == "sha256_fingerprint"

    def test_store_duplicate_hash_updates(self, temp_db, sample_hash):
        """Test that storing duplicate hash updates metadata"""
        # Store initial hash
        hash_id1 = temp_db.store_hash(
            sample_hash,
            video_id="video1",
            platform="youtube"
        )

        # Store same hash again with different metadata
        hash_id2 = temp_db.store_hash(
            sample_hash,
            video_id="video2",
            platform="tiktok"
        )

        # Should return same ID (or different ID but hash exists)
        assert hash_id2 is not None

        # Check that only one hash exists
        cursor = temp_db.conn.cursor()
        hash_str = ''.join(map(str, sample_hash.astype(int)))
        cursor.execute('SELECT COUNT(*) FROM hashes WHERE hash = ?', (hash_str,))
        count = cursor.fetchone()[0]
        assert count == 1

    def test_hash_string_conversion(self, temp_db, sample_hash):
        """Test hash is correctly converted to binary string and hex"""
        hash_id = temp_db.store_hash(sample_hash)

        cursor = temp_db.conn.cursor()
        cursor.execute('SELECT hash, hash_hex FROM hashes WHERE id = ?', (hash_id,))
        row = cursor.fetchone()

        hash_str = row[0]
        hash_hex = row[1]

        # Check binary string
        assert len(hash_str) == 256
        assert all(c in '01' for c in hash_str)

        # Check hex string
        assert len(hash_hex) == 64
        assert all(c in '0123456789abcdef' for c in hash_hex)

        # Verify conversion is correct
        expected_hash_str = ''.join(map(str, sample_hash.astype(int)))
        assert hash_str == expected_hash_str


class TestHashQuery:
    """Test hash query and similarity search"""

    def test_query_exact_match(self, temp_db, sample_hash):
        """Test querying for exact match"""
        temp_db.store_hash(sample_hash, video_id="test_video")

        # Query with same hash
        results = temp_db.query_similar(sample_hash, threshold=30)

        assert len(results) == 1
        assert results[0]['hamming_distance'] == 0
        assert results[0]['similarity'] == 100.0
        assert results[0]['video_id'] == "test_video"

    def test_query_similar_hash(self, temp_db, sample_hash):
        """Test querying for similar hashes"""
        temp_db.store_hash(sample_hash, video_id="original")

        # Create similar hash (flip 10 bits)
        similar_hash = sample_hash.copy()
        similar_hash[:10] = 1 - similar_hash[:10]

        results = temp_db.query_similar(similar_hash, threshold=30)

        assert len(results) == 1
        assert results[0]['hamming_distance'] == 10
        assert results[0]['video_id'] == "original"

    def test_query_no_match_beyond_threshold(self, temp_db, sample_hash):
        """Test that hashes beyond threshold are not returned"""
        temp_db.store_hash(sample_hash, video_id="original")

        # Create very different hash (flip 100 bits)
        different_hash = sample_hash.copy()
        different_hash[:100] = 1 - different_hash[:100]

        results = temp_db.query_similar(different_hash, threshold=30)

        assert len(results) == 0

    def test_query_platform_filter(self, temp_db, sample_hash):
        """Test platform filtering in queries"""
        # Store hashes on different platforms
        temp_db.store_hash(sample_hash, video_id="video1", platform="youtube")

        similar_hash = sample_hash.copy()
        similar_hash[0] = 1 - similar_hash[0]
        temp_db.store_hash(similar_hash, video_id="video2", platform="tiktok")

        # Query only YouTube
        results = temp_db.query_similar(sample_hash, threshold=30, platform="youtube")

        assert len(results) == 1
        assert results[0]['platform'] == "youtube"

    def test_query_result_sorting(self, temp_db, sample_hash):
        """Test that results are sorted by Hamming distance"""
        # Store exact match
        temp_db.store_hash(sample_hash, video_id="exact")

        # Store similar hash (10 bits different)
        hash_10 = sample_hash.copy()
        hash_10[:10] = 1 - hash_10[:10]
        temp_db.store_hash(hash_10, video_id="similar_10")

        # Store less similar hash (5 bits different)
        hash_5 = sample_hash.copy()
        hash_5[:5] = 1 - hash_5[:5]
        temp_db.store_hash(hash_5, video_id="similar_5")

        results = temp_db.query_similar(sample_hash, threshold=30)

        # Should be sorted by distance: 0, 5, 10
        assert len(results) == 3
        assert results[0]['hamming_distance'] == 0
        assert results[1]['hamming_distance'] == 5
        assert results[2]['hamming_distance'] == 10

    def test_query_limit(self, temp_db, sample_hash):
        """Test query result limit"""
        # Store multiple similar hashes
        for i in range(10):
            similar_hash = sample_hash.copy()
            similar_hash[i] = 1 - similar_hash[i]
            temp_db.store_hash(similar_hash, video_id=f"video_{i}")

        results = temp_db.query_similar(sample_hash, threshold=30, limit=5)

        assert len(results) == 5


class TestDatabaseStats:
    """Test database statistics"""

    def test_stats_empty_database(self, temp_db):
        """Test stats for empty database"""
        stats = temp_db.get_stats()

        assert stats['total_hashes'] == 0
        assert stats['by_platform'] == {}
        assert stats['oldest_entry'] is None
        assert stats['newest_entry'] is None

    def test_stats_with_data(self, temp_db, sample_hash):
        """Test stats with stored hashes"""
        # Store hashes on different platforms
        temp_db.store_hash(sample_hash, platform="youtube")

        hash2 = sample_hash.copy()
        hash2[0] = 1 - hash2[0]
        temp_db.store_hash(hash2, platform="youtube")

        hash3 = sample_hash.copy()
        hash3[1] = 1 - hash3[1]
        temp_db.store_hash(hash3, platform="tiktok")

        stats = temp_db.get_stats()

        assert stats['total_hashes'] == 3
        assert stats['by_platform']['youtube'] == 2
        assert stats['by_platform']['tiktok'] == 1
        assert stats['oldest_entry'] is not None
        assert stats['newest_entry'] is not None


class TestHashDeletion:
    """Test hash deletion"""

    def test_delete_existing_hash(self, temp_db, sample_hash):
        """Test deleting an existing hash"""
        hash_id = temp_db.store_hash(sample_hash)

        success = temp_db.delete_hash(hash_id)

        assert success is True

        # Verify deletion
        cursor = temp_db.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM hashes WHERE id = ?', (hash_id,))
        count = cursor.fetchone()[0]
        assert count == 0

    def test_delete_nonexistent_hash(self, temp_db):
        """Test deleting nonexistent hash"""
        success = temp_db.delete_hash(99999)

        assert success is False


class TestContextManager:
    """Test context manager functionality"""

    def test_context_manager_usage(self, sample_hash):
        """Test using database as context manager"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_path = temp_file.name
        temp_file.close()

        with HashDatabase(temp_path) as db:
            hash_id = db.store_hash(sample_hash)
            assert hash_id is not None

        # Database should be closed
        Path(temp_path).unlink()


class TestMetadataHandling:
    """Test metadata serialization and deserialization"""

    def test_metadata_json_serialization(self, temp_db, sample_hash):
        """Test that metadata is properly JSON serialized"""
        metadata = {
            "resolution": "1080p",
            "tags": ["test", "sample"],
            "nested": {"key": "value"}
        }

        hash_id = temp_db.store_hash(sample_hash, metadata=metadata)

        # Query back
        results = temp_db.query_similar(sample_hash, threshold=0)

        assert len(results) == 1
        assert results[0]['metadata'] == metadata

    def test_null_metadata(self, temp_db, sample_hash):
        """Test storing hash without metadata"""
        hash_id = temp_db.store_hash(sample_hash)

        results = temp_db.query_similar(sample_hash, threshold=0)

        assert len(results) == 1
        assert results[0]['metadata'] is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
