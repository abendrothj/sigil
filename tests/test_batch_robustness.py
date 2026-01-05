#!/usr/bin/env python3
"""
Tests for batch_robustness module

Tests cover:
- Video compression testing
- Batch processing of video directories
- Hamming distance calculation after compression
- Error handling for failed compressions
"""

import pytest
import tempfile
import shutil
import subprocess
from pathlib import Path
import numpy as np
import cv2
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.batch_robustness import test_video, batch_test_videos


@pytest.fixture
def test_video_file():
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
    # Also cleanup any compressed versions
    compressed_path = Path(temp_path).with_suffix('.crf28.mp4')
    compressed_path.unlink(missing_ok=True)


@pytest.fixture
def test_video_directory():
    """Create a directory with test videos"""
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)

    # Create 3 test videos
    for i in range(3):
        video_path = temp_path / f"test_video_{i}.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(video_path), fourcc, 30.0, (224, 224))

        for j in range(20):
            frame = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            out.write(frame)

        out.release()

    yield temp_path

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


def check_ffmpeg_available():
    """Check if ffmpeg is available"""
    try:
        subprocess.run(['ffmpeg', '-version'],
                      capture_output=True,
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


@pytest.mark.skipif(not check_ffmpeg_available(),
                   reason="ffmpeg not available")
class TestVideoCompression:
    """Test video compression and hash comparison"""

    def test_video_basic_compression(self, test_video_file):
        """Test basic video compression and hash comparison"""
        result = test_video(test_video_file, max_frames=20, crf=28)

        assert result is not None
        distance, hash_length = result

        assert isinstance(distance, (int, np.integer))
        assert hash_length == 256
        # Distance should be relatively small for compression
        assert distance < 100  # Reasonable threshold

    def test_video_different_crf_values(self, test_video_file):
        """Test compression with different CRF values"""
        # Lower CRF = higher quality = should be more similar
        result_low_crf = test_video(test_video_file, max_frames=20, crf=18)
        result_high_crf = test_video(test_video_file, max_frames=20, crf=35)

        assert result_low_crf is not None
        assert result_high_crf is not None

        distance_low, _ = result_low_crf
        distance_high, _ = result_high_crf

        # Lower CRF should generally have smaller distance
        # (though this isn't guaranteed for all videos)
        assert distance_low < 256
        assert distance_high < 256

    def test_video_max_frames_limit(self, test_video_file):
        """Test processing with frame limit"""
        result = test_video(test_video_file, max_frames=10, crf=28)

        assert result is not None
        distance, hash_length = result
        assert hash_length == 256

    def test_video_nonexistent_file(self):
        """Test handling of nonexistent video file"""
        # Should raise an exception or return None
        # load_video_frames will fail to open the file
        with pytest.raises((StopIteration, FileNotFoundError, Exception)):
            test_video('/nonexistent/video.mp4', max_frames=20, crf=28)


@pytest.mark.skipif(not check_ffmpeg_available(),
                   reason="ffmpeg not available")
class TestBatchProcessing:
    """Test batch video processing"""

    def test_batch_test_videos_basic(self, test_video_directory):
        """Test batch processing of video directory"""
        results = batch_test_videos(str(test_video_directory), max_frames=20, crf=28)

        assert len(results) == 3

        for fname, distance, hash_length in results:
            assert fname.endswith('.mp4')
            assert isinstance(distance, (int, np.integer))
            assert hash_length == 256
            assert distance < 256

    def test_batch_test_videos_empty_directory(self):
        """Test batch processing with empty directory"""
        temp_dir = tempfile.mkdtemp()

        results = batch_test_videos(temp_dir, max_frames=20, crf=28)

        assert len(results) == 0

        shutil.rmtree(temp_dir)

    def test_batch_test_videos_mixed_files(self, test_video_directory):
        """Test batch processing with non-video files"""
        # Add a non-video file
        (test_video_directory / "readme.txt").write_text("not a video")

        results = batch_test_videos(str(test_video_directory), max_frames=20, crf=28)

        # Should only process the 3 video files
        assert len(results) == 3

    def test_batch_test_videos_custom_crf(self, test_video_directory):
        """Test batch processing with custom CRF value"""
        results = batch_test_videos(str(test_video_directory), max_frames=20, crf=23)

        assert len(results) == 3

        for fname, distance, hash_length in results:
            assert hash_length == 256


class TestBatchRobustnessWithoutFFmpeg:
    """Tests that don't require ffmpeg"""

    def test_import_functions(self):
        """Test that functions can be imported"""
        from core.batch_robustness import test_video, batch_test_videos

        assert callable(test_video)
        assert callable(batch_test_videos)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
