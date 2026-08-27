import numpy as np
import cv2

from collections import defaultdict
import argparse
import pickle
import sys


def parse_args():
    parser = argparse.ArgumentParser("Image to ASCII")
    parser.add_argument("-i", "--image", default="0", type=str,
                        help="input image or 0,1,2,etc. for webcam (default: 0)")
    parser.add_argument("-o", "--output", type=str,
                        default=None, help="output text file (default: sys.stdout)")
    parser.add_argument("-n", "--num_cols", type=int, default=0,
                        help="number of character for output's width (default: maximum resolution)")
    parser.add_argument("-c","--characters", type=str ,help="characters to include (default: ASCII)", 
                        default="!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~")
    args = parser.parse_args()
    return args


def webcam(cam):
    cap = cv2.VideoCapture(cam)
    message = "Press space to capture"
    cv2.namedWindow(message)
    while True:
        ret, frame = cap.read()
        if not ret:
            raise RuntimeError("failed to initialise camera")
        cv2.imshow(message, frame)
        k = cv2.waitKey(1)
        if k % 256 == 32:
            break
    cap.release()
    cv2.destroyAllWindows()
    return frame


def main(opt):
    try:
        image = webcam(int(opt.image))
    except ValueError:
        image = cv2.imread(opt.image)

    if image is None:
        raise RuntimeError("failed to load image")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    with open("characters.pickle", "rb") as characters_file:
        characters_map = pickle.load(characters_file)

    characters = defaultdict(list)
    for char in opt.characters + " ":
        characters[characters_map.get(char,-1)].append(char)

    keys = np.sort(list(characters.keys()))

    num_cols = opt.num_cols or np.inf
    height, width = image.shape
    cell_width = width / num_cols
    cell_height = 2 * cell_width or np.inf
    num_rows = int(height / cell_height)

    if num_cols > width or num_rows > height:
        cell_width = 1
        cell_height = 2
        num_cols = int(width / cell_width)
        num_rows = int(height / cell_height)

    with (open(opt.output, "w", encoding="utf-8") if opt.output else sys.stdout) as output_file:
        for i in range(num_rows):
            for j in range(num_cols):
                output_file.write(
                    np.random.choice(
                        characters[keys[np.searchsorted(keys, max(keys) * (1-np.mean(image[int(i * cell_height):int(
                            (i + 1) * cell_height), int(j * cell_width):int((j + 1) * cell_width)])/255))]]
                    )
                )
            output_file.write("\n")


if __name__ == '__main__':
    opt = parse_args()
    main(opt)
