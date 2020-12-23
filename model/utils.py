# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import

import os
import glob

import cv2
import imageio
import scipy.misc as misc
from skimage import transform
import numpy as np
from io import StringIO, BytesIO


def pad_seq(seq, batch_size):
    # pad the sequence to be the multiples of batch_size
    seq_len = len(seq)
    if seq_len % batch_size == 0:
        return seq
    padded = batch_size - (seq_len % batch_size)
    seq.extend(seq[:padded])
    return seq


def bytes_to_file(bytes_img):
    return BytesIO(bytes_img)


def normalize_image(img):
    """
    Make image zero centered and in between (-1, 1)
    """
    normalized = (img / 127.5) - 1.
    return normalized


def read_split_image(img):
    mat = imageio.imread(img).astype(np.uint8)
    side = int(mat.shape[1] / 2)
    assert side * 2 == mat.shape[1]
    img_A = mat[:, :side]  # target
    img_B = mat[:, side:]  # source

    return img_A, img_B


def shift_and_resize_image(img, shift_x, shift_y, nw, nh):
    w, h = img.shape
    enlarged = cv2.resize(img, (nw, nh))
    return enlarged[shift_x:shift_x + w, shift_y:shift_y + h]

def rotate_image(img, rotate_angle):
    img = transform.rotate(img, rotate_angle, cval=255, preserve_range=True)
    return img

def scale_back(images):
    return (images + 1.) / 2.


def merge(images, size):
    h, w = images.shape[2], images.shape[3]
    img = np.zeros((h * size[0], w * size[1]))
    for idx, image in enumerate(images):
        i = idx % size[1]
        j = idx // size[1]
        img[j * h:j * h + h, i * w:i * w + w] = image

    return img


def save_concat_images(imgs, img_path):
    concated = np.concatenate(imgs, axis=1)
    imageio.imsave(img_path, concated)


def compile_frames_to_gif(frame_dir, gif_file):
    frames = sorted(glob.glob(os.path.join(frame_dir, "*.png")))
    print(frames)
    images = [imageio.imresize(imageio.imread(f), interp='nearest', size=0.33) for f in frames]
    imageio.imsave(gif_file, images, duration=0.2)
    return gif_file
