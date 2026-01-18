"""
Functions for working with images and colors
"""

import logging
import math
from PIL import Image

logger = logging.getLogger(__name__)


def average_rgb(image: Image.Image):
    """
    Compute the average R, G, B values of an image.

    Returns:
        (r_avg, g_avg, b_avg) as floats in [0, 255].
    """
    pixels = list(image.convert("RGB").getdata())
    n = len(pixels)

    r = sum(p[0] for p in pixels) / n
    g = sum(p[1] for p in pixels) / n
    b = sum(p[2] for p in pixels) / n

    return r, g, b


def luminance_bt709(image: Image.Image):
    """
    Compute perceived luminance using ITU-R BT.709 coefficients.

    Formula:
        Y = 0.2126 R + 0.7152 G + 0.0722 B
    """
    r, g, b = average_rgb(image)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def relative_luminance(image: Image.Image):
    """
    Compute WCAG relative luminance (0–1 scale).

    Converts sRGB to linear light first.
    """
    def srgb_to_linear(c):
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055)**2.4

    r, g, b = average_rgb(image)
    R = srgb_to_linear(r)
    G = srgb_to_linear(g)
    B = srgb_to_linear(b)

    return 0.2126 * R + 0.7152 * G + 0.0722 * B


def brightness_hsp(image: Image.Image):
    """
    Compute perceived brightness using the HSP model.

    Formula:
        brightness = sqrt(0.299 R^2 + 0.587 G^2 + 0.114 B^2)
    """
    r, g, b = average_rgb(image)
    return math.sqrt(0.299 * r * r + 0.587 * g * g + 0.114 * b * b)


def colorfulness(image: Image.Image):
    """
    Compute image colorfulness using the Hasler–Süsstrunk metric.
    """
    pixels = list(image.convert("RGB").getdata())
    rg = [(p[0] - p[1]) for p in pixels]
    yb = [(0.5 * (p[0] + p[1]) - p[2]) for p in pixels]

    mean_rg = sum(rg) / len(rg)
    mean_yb = sum(yb) / len(yb)

    std_rg = (sum((x - mean_rg)**2 for x in rg) / len(rg))**0.5
    std_yb = (sum((x - mean_yb)**2 for x in yb) / len(yb))**0.5

    return math.sqrt(std_rg**2 + std_yb**2) + 0.3 * math.sqrt(mean_rg**2 + mean_yb**2)


def rms_contrast(image: Image.Image):
    """
    Compute RMS contrast of an image (grayscale).
    """
    gray = image.convert("L")
    pixels = list(gray.getdata())
    mean = sum(pixels) / len(pixels)
    variance = sum((p - mean)**2 for p in pixels) / len(pixels)
    return math.sqrt(variance)


def rgb_histograms(image: Image.Image):
    """
    Return histograms for R, G, B channels (256 bins each).
    """
    r, g, b = image.convert("RGB").split()
    return r.histogram(), g.histogram(), b.histogram()


def analyze_image(image: Image.Image):
    """
    Return a dictionary of useful image statistics.
    """
    return {
        "average_rgb": average_rgb(image),
        "luminance_bt709": luminance_bt709(image),
        "relative_luminance": relative_luminance(image),
        "brightness_hsp": brightness_hsp(image),
        "colorfulness": colorfulness(image),
        "rms_contrast": rms_contrast(image),
    }


def crop_image(image, left, top, right, bottom):
    """
    Crop an image to the given bounding box.
    Coordinates follow PIL convention.
    """
    return image.crop((left, top, right, bottom))


def resize_image(image, width=None, height=None, keep_aspect=True):
    """
    Resize an image. If keep_aspect=True, one dimension may be None.
    """
    if keep_aspect:
        if width is None and height is None:
            raise ValueError("Specify width or height when keep_aspect=True")

        w, h = image.size
        if width is not None:
            scale = width / w
            height = int(h * scale)
        else:
            scale = height / h
            width = int(w * scale)

    return image.resize((width, height), Image.LANCZOS)


def sobel_edges(image):
    """
    Compute Sobel edge magnitude image (grayscale).
    Returns a new grayscale PIL image.
    """
    gray = image.convert("L")
    w, h = gray.size
    pixels = gray.load()

    out = Image.new("L", (w, h))
    out_px = out.load()

    # Sobel kernels
    Gx = [[-1, 0, 1],
          [-2, 0, 2],
          [-1, 0, 1]]

    Gy = [[1, 2, 1],
          [0, 0, 0],
          [-1, -2, -1]]

    for y in range(1, h - 1):
        for x in range(1, w - 1):
            sx = 0
            sy = 0
            for ky in range(-1, 2):
                for kx in range(-1, 2):
                    p = pixels[x + kx, y + ky]
                    sx += p * Gx[ky + 1][kx + 1]
                    sy += p * Gy[ky + 1][kx + 1]

            mag = int(min(255, (sx * sx + sy * sy)**0.5))
            out_px[x, y] = mag

    return out


import random


def quantize_kmeans(image, k=8, iterations=10):
    """
    Simple k-means color quantization.
    Returns a new RGB image with k colors.
    """
    img = image.convert("RGB")
    pixels = list(img.getdata())

    # Initialize cluster centers randomly
    centers = random.sample(pixels, k)

    for _ in range(iterations):
        clusters = {i: [] for i in range(k)}

        # Assign pixels to nearest center
        for p in pixels:
            distances = [(i, (p[0] - c[0])**2 + (p[1] - c[1])**2 + (p[2] - c[2])**2)
                         for i, c in enumerate(centers)]
            idx = min(distances, key=lambda x: x[1])[0]
            clusters[idx].append(p)

        # Recompute centers
        new_centers = []
        for i in range(k):
            if clusters[i]:
                r = sum(p[0] for p in clusters[i]) / len(clusters[i])
                g = sum(p[1] for p in clusters[i]) / len(clusters[i])
                b = sum(p[2] for p in clusters[i]) / len(clusters[i])
                new_centers.append((int(r), int(g), int(b)))
            else:
                new_centers.append(centers[i])

        centers = new_centers

    # Recolor image
    new_pixels = []
    for p in pixels:
        distances = [(i, (p[0] - c[0])**2 + (p[1] - c[1])**2 + (p[2] - c[2])**2)
                     for i, c in enumerate(centers)]
        idx = min(distances, key=lambda x: x[1])[0]
        new_pixels.append(centers[idx])

    out = Image.new("RGB", img.size)
    out.putdata(new_pixels)
    return out
