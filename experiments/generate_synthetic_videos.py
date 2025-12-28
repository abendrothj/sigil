import cv2
import numpy as np
import os

def make_solid_color_video(path, color, num_frames=30, size=(128, 128), fps=15):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(path, fourcc, fps, size)
    for _ in range(num_frames):
        frame = np.full((size[1], size[0], 3), color, dtype=np.uint8)
        out.write(frame)
    out.release()

def make_moving_square_video(path, num_frames=30, size=(128, 128), fps=15):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(path, fourcc, fps, size)
    for i in range(num_frames):
        frame = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        x = int((size[0] - 32) * i / (num_frames - 1))
        y = int((size[1] - 32) * i / (num_frames - 1))
        cv2.rectangle(frame, (x, y), (x+32, y+32), (0, 255, 0), -1)
        out.write(frame)
    out.release()

def make_noise_video(path, num_frames=30, size=(128, 128), fps=15):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(path, fourcc, fps, size)
    for _ in range(num_frames):
        frame = np.random.randint(0, 256, (size[1], size[0], 3), dtype=np.uint8)
        out.write(frame)
    out.release()

def make_gradient_video(path, num_frames=30, size=(128, 128), fps=15):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(path, fourcc, fps, size)
    for i in range(num_frames):
        frame = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        alpha = i / (num_frames - 1)
        for c in range(3):
            frame[..., c] = np.uint8(255 * (alpha if c == 0 else 1 - alpha))
        out.write(frame)
    out.release()

def main():
    out_dir = "test_batch_input"
    os.makedirs(out_dir, exist_ok=True)
    make_solid_color_video(os.path.join(out_dir, "solid_red.mp4"), (0, 0, 255))
    make_solid_color_video(os.path.join(out_dir, "solid_green.mp4"), (0, 255, 0))
    make_solid_color_video(os.path.join(out_dir, "solid_blue.mp4"), (255, 0, 0))
    make_moving_square_video(os.path.join(out_dir, "moving_square.mp4"))
    make_noise_video(os.path.join(out_dir, "noise.mp4"))
    make_gradient_video(os.path.join(out_dir, "gradient.mp4"))
    print("Synthetic videos generated in test_batch_input/")

if __name__ == "__main__":
    main()
