import cv2
import numpy as np
import os

def make_varied_test_videos():
    out_dir = "test_batch_input"
    os.makedirs(out_dir, exist_ok=True)
    # 1. Moving square, 120 frames (8 seconds at 15 fps)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    path1 = os.path.join(out_dir, "long_moving_square.mp4")
    out1 = cv2.VideoWriter(path1, fourcc, 15, (128, 128))
    for i in range(120):
        frame = np.zeros((128, 128, 3), dtype=np.uint8)
        x = int((128 - 32) * i / 119)
        y = int((128 - 32) * (119 - i) / 119)
        cv2.rectangle(frame, (x, y), (x+32, y+32), (0, 255, 0), -1)
        out1.write(frame)
    out1.release()
    # 2. Color cycling, 150 frames (10 seconds at 15 fps)
    path2 = os.path.join(out_dir, "long_color_cycle.mp4")
    out2 = cv2.VideoWriter(path2, fourcc, 15, (128, 128))
    for i in range(150):
        color = [int(127.5 + 127.5 * np.sin(2 * np.pi * i / 50 + phase)) for phase in (0, 2, 4)]
        frame = np.full((128, 128, 3), color, dtype=np.uint8)
        out2.write(frame)
    out2.release()
    # 3. Gradient + noise, 180 frames (12 seconds at 15 fps)
    path3 = os.path.join(out_dir, "long_gradient_noise.mp4")
    out3 = cv2.VideoWriter(path3, fourcc, 15, (128, 128))
    for i in range(180):
        grad = np.tile(np.linspace(0, 255, 128, dtype=np.uint8), (128, 1))
        frame = np.stack([grad, np.flipud(grad), np.roll(grad, i % 128, axis=1)], axis=2)
        noise = np.random.randint(0, 32, (128, 128, 3), dtype=np.uint8)
        frame = cv2.add(frame, noise)
        out3.write(frame)
    out3.release()
    print("Longer test videos generated in test_batch_input/")

if __name__ == "__main__":
    make_varied_test_videos()
