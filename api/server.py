#!/usr/bin/env python3
"""
Basilisk API Server
Flask backend for perceptual hash tracking service
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import sys
import json
import hashlib
from pathlib import Path
import tempfile
import numpy as np

# Add core to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from core.perceptual_hash import load_video_frames, extract_perceptual_features, compute_perceptual_hash, hamming_distance
    from core.hash_database import HashDatabase
except ImportError as e:
    print(f"Error importing core modules: {e}")
    print("Make sure core/ is in the correct location")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max for videos
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
TEMP_DIR = Path(tempfile.gettempdir()) / 'basilisk'
TEMP_DIR.mkdir(exist_ok=True)

# Initialize database
DB_PATH = Path(__file__).parent.parent / 'basilisk_hashes.db'
db = HashDatabase(str(DB_PATH))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'basilisk-hash-api',
        'version': '1.0.0',
        'feature': 'perceptual_hash_tracking'
    })


@app.route('/api/extract', methods=['POST'])
def extract_hash():
    """
    Extract perceptual hash from uploaded video

    Request:
        - video: File upload
        - max_frames: int (optional, default 60)
        - metadata: JSON string (optional)

    Response:
        - success: bool
        - hash: 256-bit hash as string
        - hash_id: unique identifier
        - metadata: stored metadata
    """
    try:
        # Validate request
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400

        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Use MP4, AVI, MOV, or MKV'}), 400

        # Get parameters
        max_frames = int(request.form.get('max_frames', 60))
        metadata_str = request.form.get('metadata', '{}')
        metadata = json.loads(metadata_str)

        # Validate max_frames
        if max_frames < 10 or max_frames > 300:
            return jsonify({'error': 'max_frames must be between 10 and 300'}), 400

        # Generate unique ID
        request_id = hashlib.sha256(os.urandom(32)).hexdigest()[:16]

        # Save uploaded file
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        input_path = TEMP_DIR / f"{request_id}_input.{ext}"

        file.save(str(input_path))

        # Extract hash
        print(f"Extracting hash from {filename} with max_frames={max_frames}")
        frames = load_video_frames(str(input_path), max_frames=max_frames)

        if not frames:
            input_path.unlink(missing_ok=True)
            return jsonify({'error': 'Failed to load video frames'}), 400

        features = extract_perceptual_features(frames)
        hash_bits = compute_perceptual_hash(features)

        # Convert to string
        hash_str = ''.join(map(str, hash_bits))

        # Store in database
        metadata['original_filename'] = filename
        metadata['num_frames'] = len(frames)
        hash_id = db.store_hash(
            hash_bits,
            file_path=str(input_path),
            frame_count=len(frames),
            metadata=metadata
        )

        # Clean up
        input_path.unlink(missing_ok=True)

        return jsonify({
            'success': True,
            'hash': hash_str,
            'hash_id': hash_id,
            'num_frames': len(frames),
            'metadata': metadata
        })

    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        print(f"Error in extract_hash: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/compare', methods=['POST'])
def compare_hash():
    """
    Compare video hash against database

    Request:
        - video: File upload OR hash: string
        - threshold: int (optional, default 30)

    Response:
        - success: bool
        - matches: list of matching hashes
        - closest_distance: minimum hamming distance
    """
    try:
        threshold = int(request.form.get('threshold', 30))

        # Get hash either from video or direct input
        if 'hash' in request.form:
            hash_str = request.form['hash']
            if len(hash_str) != 256 or not all(c in '01' for c in hash_str):
                return jsonify({'error': 'Invalid hash format. Must be 256-bit binary string'}), 400
            hash_bits = [int(c) for c in hash_str]
        elif 'video' in request.files:
            file = request.files['video']
            if not allowed_file(file.filename):
                return jsonify({'error': 'Invalid file type'}), 400

            max_frames = int(request.form.get('max_frames', 60))
            request_id = hashlib.sha256(os.urandom(32)).hexdigest()[:16]
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower()
            input_path = TEMP_DIR / f"{request_id}_input.{ext}"

            file.save(str(input_path))
            frames = load_video_frames(str(input_path), max_frames=max_frames)
            input_path.unlink(missing_ok=True)

            if not frames:
                return jsonify({'error': 'Failed to load video frames'}), 400

            features = extract_perceptual_features(frames)
            hash_bits = compute_perceptual_hash(features)
            hash_str = ''.join(map(str, hash_bits))
        else:
            return jsonify({'error': 'Provide either video file or hash string'}), 400

        # Find matches - convert hash_str back to numpy array for query_similar
        hash_bits_for_query = np.array([int(c) for c in hash_str])
        matches = db.query_similar(hash_bits_for_query, threshold=threshold)

        # Calculate closest distance
        closest_distance = min([m['hamming_distance'] for m in matches]) if matches else 256

        return jsonify({
            'success': True,
            'query_hash': hash_str,
            'matches': matches,
            'num_matches': len(matches),
            'closest_distance': closest_distance,
            'threshold': threshold
        })

    except Exception as e:
        print(f"Error in compare_hash: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        stats = db.get_stats()
        return jsonify({
            'success': True,
            'total_hashes': stats['total_hashes'],
            'by_platform': stats['by_platform'],
            'oldest_entry': stats['oldest_entry'],
            'newest_entry': stats['newest_entry'],
            'database_path': str(DB_PATH)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("🐍 Basilisk Perceptual Hash Tracking API")
    print("=" * 60)
    print("Starting Flask server on http://localhost:5000")
    print("Endpoints:")
    print("  GET  /health          - Health check")
    print("  POST /api/extract     - Extract perceptual hash from video")
    print("  POST /api/compare     - Compare hash against database")
    print("  GET  /api/stats       - Database statistics")
    print("=" * 60)
    print()
    print("NOTE: This API uses a FIXED SEED (42) for hash generation.")
    print("WARNING: Fixed seed means hashes are reproducible but not cryptographically secure.")
    print("Anyone with access to this code can compute the same hash for any video.")
    print("=" * 60)

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
