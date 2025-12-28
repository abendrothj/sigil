import os
import urllib.request

# Example: Download a few UCF101 sample videos (public domain, action recognition benchmark)
def download_ucf101_samples():
    out_dir = "test_batch_input"
    os.makedirs(out_dir, exist_ok=True)
    # A few handpicked UCF101 sample URLs (short, public)
    videos = [
        ("https://crcv.ucf.edu/THUMOS14/UCF101/UCF101/v_PlayingGuitar_g01_c01.avi", "ucf_playing_guitar.avi"),
        ("https://crcv.ucf.edu/THUMOS14/UCF101/UCF101/v_ApplyEyeMakeup_g01_c01.avi", "ucf_eye_makeup.avi"),
        ("https://crcv.ucf.edu/THUMOS14/UCF101/UCF101/v_Basketball_g01_c01.avi", "ucf_basketball.avi"),
    ]
    for url, fname in videos:
        out_path = os.path.join(out_dir, fname)
        if not os.path.exists(out_path):
            print(f"Downloading {fname}...")
            urllib.request.urlretrieve(url, out_path)
            print(f"Saved to {out_path}")
        else:
            print(f"{fname} already exists.")
    print("UCF101 sample videos ready.")

if __name__ == "__main__":
    download_ucf101_samples()
