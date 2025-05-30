#!/usr/bin/python3
# -*-coding:utf-8-*-

import numpy as np
import skimage.color, skimage.transform, skimage.filters, skimage.feature
import skimage as ski
import pilkit.processors
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import numba
import config


def _pack_block(bits_str: str) -> bytearray:
    # bits_str are human way (MSB:LSB) of representing binary numbers (e.g. "1010" means 12)
    if len(bits_str) % 8 != 0:
        raise ValueError("bits_str should have the length of ")
    partitioned_str = [bits_str[i:i + 8] for i in range(0, len(bits_str), 8)]
    int_str = [int(i, 2) for i in partitioned_str]
    return bytes(int_str)


def binimage2bitstream(bin_image: np.ndarray):
    # bin_image is a numpy int array consists of only 1s and 0s
    # input follows thermal printer's mechanism: 1 is black (printed) and 0 is white (left untouched)
    assert bin_image.max() <= 1 and bin_image.min() >= 0
    return _pack_block(''.join(map(str, bin_image.flatten())))


def im2binimage(im, conversion="threshold"):
    # convert standard numpy array image to bin_image
    fixed_width = 384
    if hasattr(config, "width"):
        fixed_width = config.width
    if (len(im.shape) != 2):
        im = ski.color.rgb2gray(im)
    im = ski.transform.resize(im, (round(fixed_width / im.shape[1] * im.shape[0]), fixed_width))
    if conversion == "threshold":
        ret = (im > ski.filters.threshold_li(im)).astype(int)  # Invert threshold logic
    elif conversion == "edge":
        ret = (ski.feature.canny(im, sigma=2)).astype(int)  # Ensure edges are 1
    else:
        raise ValueError("Unsupported conversion method")
    return ret

# this is straight from https://github.com/tgray/hyperdither
@numba.jit
def dither(num, thresh=127):
    derr = np.zeros(num.shape, dtype=np.int32)  # Use np.int32 or np.int64

    div = 8
    for y in range(num.shape[0]):
        for x in range(num.shape[1]):
            newval = derr[y, x] + num[y, x]
            if newval >= thresh:
                errval = newval - 255
                num[y, x] = 1.0  # Black
            else:
                errval = newval
                num[y, x] = 0.0  # White
            if x + 1 < num.shape[1]:
                derr[y, x + 1] += errval / div
                if x + 2 < num.shape[1]:
                    derr[y, x + 2] += errval / div
            if y + 1 < num.shape[0]:
                derr[y + 1, x - 1] += errval / div
                derr[y + 1, x] += errval / div
                if y + 2 < num.shape[0]:
                    derr[y + 2, x] += errval / div
                if x + 1 < num.shape[1]:
                    derr[y + 1, x + 1] += errval / div
    return num[::-1, :] * 255

def im2binimage2(im):
    basewidth = 384
    img = Image.open(im).convert('L')
    
    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((basewidth, hsize), Image.Resampling.LANCZOS)

    m = np.array(img)[:, :]
    m2 = dither(m)
    
    # Convert the array to uint8 before creating the image
    m2 = m2.astype(np.uint8)
    out = Image.fromarray(m2[::-1, :])
    # out.show()

    enhancer = ImageEnhance.Contrast(out)
    enhanced_img = enhancer.enhance(4.0)
    # enhanced_img.show()

    np_img = np.array(enhanced_img).astype(int)
    
    # Ensure np_img contains only 0 and 1
    np_img = (np_img < 127).astype(int)  # Invert binary logic here

    return binimage2bitstream(np_img)

def sirius(im):
    np_img = np.fromfile(im, dtype='uint8')
    # there must be a less stupid way to invert the array but i am baby
    np_img[np_img == 1] = 100
    np_img[np_img == 0] = 1
    np_img[np_img == 100] = 0
    return binimage2bitstream(np_img)
