import cv2
import numpy as np

def make_short_test_video(path, num_frames=10, size=(128, 128), fps=15):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(path, fourcc, fps, size)
    for i in range(num_frames):
        frame = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        x = int((size[0] - 32) * i / (num_frames - 1))
        y = int((size[1] - 32) * i / (num_frames - 1))
        cv2.rectangle(frame, (x, y), (x+32, y+32), (0, 255, 0), -1)
        out.write(frame)
    out.release()
    print(f"Short test video saved to {path}")

if __name__ == "__main__":
    make_short_test_video("short_test.mp4")
