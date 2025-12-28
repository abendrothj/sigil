import urllib.request
import os

def download_video(url, out_path):
    print(f"Downloading {url} to {out_path}...")
    urllib.request.urlretrieve(url, out_path)
    print("Done.")

def main():
    out_dir = "test_batch_input"
    os.makedirs(out_dir, exist_ok=True)
    videos = [
        ("https://sample-videos.com/video123/mp4/240/big_buck_bunny_240p_1mb.mp4", "big_buck_bunny.mp4"),
        ("https://sample-videos.com/video123/mp4/240/sample_960x400_ocean_with_audio.mp4", "ocean.mp4"),
        ("https://sample-videos.com/video123/mp4/240/sample_960x400_flower.mp4", "flower.mp4"),
    ]
    for url, fname in videos:
        out_path = os.path.join(out_dir, fname)
        if not os.path.exists(out_path):
            download_video(url, out_path)
        else:
            print(f"{fname} already exists.")
    print("All sample videos downloaded.")

if __name__ == "__main__":
    main()
