import subprocess
import os
import sys

def compress_h264(input_path, output_path, crf=28):
    """Compresses a video using H.264 codec at specified CRF."""
    cmd = [
        'ffmpeg', '-y', '-i', input_path,
        '-c:v', 'libx264', '-preset', 'medium', '-crf', str(crf),
        '-an', output_path
    ]
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print("Compression failed:", result.stderr.decode())
        sys.exit(1)
    print(f"Compressed video saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python compress_video.py <input_video> <output_video> [crf]")
        sys.exit(1)
    input_video = sys.argv[1]
    output_video = sys.argv[2]
    crf = int(sys.argv[3]) if len(sys.argv) > 3 else 28
    compress_h264(input_video, output_video, crf)
