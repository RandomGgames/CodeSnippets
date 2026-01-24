"""
Functions for working with images and colors
"""

import logging
import math
import tkinter as tk
from PIL import Image, ImageTk

import numpy as np

logger = logging.getLogger(__name__)


def _validate_image(image: Image.Image) -> Image.Image:
    """
    Validate that the input is a non-empty PIL image and return it.

    Raises:
        TypeError: If not a PIL Image.
        ValueError: If image has zero area.
    """
    if not isinstance(image, Image.Image):
        raise TypeError("image must be a PIL.Image.Image instance")

    if image.width <= 0 or image.height <= 0:
        raise ValueError("image must have non-zero width and height")

    return image


def average_rgb(image: Image.Image, *, normalize: bool = False, numpy_threshold: int = 40_000) -> tuple[float, float, float]:
    """
    Compute the average RGB color of an image.

    Automatically selects the fastest backend based on image size.

    This function looks at every pixel in the image and computes the
    average red, green, and blue channel values.

    Conceptually, this answers:
        "If the entire image were replaced by a single solid color,
         what color would best represent it?"

    Args:
        image: PIL Image
        normalize:
            - False: return values in [0, 255]
            - True: return values in [0.0, 1.0]
        numpy_threshold: Minimum pixel count to prefer NumPy. Defaults to 40,000 ( ~200x200 pixels ).

    Returns:
        (r, g, b) as floats
    """
    image = _validate_image(image)
    rgb = image.convert("RGB")

    pixel_count = rgb.width * rgb.height

    use_numpy = pixel_count >= numpy_threshold

    if use_numpy:
        try:
            arr = np.asarray(rgb, dtype=np.float32)
            mean = arr.mean(axis=(0, 1))
            r, g, b = float(mean[0]), float(mean[1]), float(mean[2])
            logger.debug(
                "average_rgb: NumPy backend (%d pixels)", pixel_count
            )
        except Exception:
            logger.debug("average_rgb: NumPy failed, falling back to PIL loop")
            use_numpy = False

    if not use_numpy:
        pixels = rgb.getdata()
        n = pixel_count

        r = g = b = 0.0
        for pr, pg, pb in pixels:
            r += pr
            g += pg
            b += pb

        r /= n
        g /= n
        b /= n

        logger.debug(
            "average_rgb: PIL backend (%d pixels)", pixel_count
        )

    if normalize:
        inv = 1.0 / 255.0
        return r * inv, g * inv, b * inv

    return r, g, b


def luminance_bt709(image: Image.Image) -> float:
    """
    Estimate how bright an image appears to a human viewer.

    This uses the ITU-R BT.709 luminance formula, which applies different
    weights to red, green, and blue based on human visual sensitivity.

    Humans perceive green as much brighter than blue, and somewhat
    brighter than red. This weighting reflects that behavior.

    Conceptually, this answers:
        "How bright does this image *look*, on average?"

    Returns:
        A single brightness value in the range [0-255].
    """
    r, g, b = average_rgb(image)
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    logger.debug("BT.709 luminance: %.3f", y)
    return y


def relative_luminance(image: Image.Image) -> float:
    """
    Compute the relative luminance of an image on a 0-1 scale.

    Relative luminance measures perceived brightness in *linear light*.
    Unlike BT.709 luminance, this function first removes gamma correction
    from sRGB values before applying luminance weights.

    This metric is defined by the WCAG accessibility standards and is used
    to compute contrast ratios for readable text and UI design.

    Conceptually, this answers:
        "How much actual light energy does this image represent,
         as perceived by a human eye?"

    Returns:
        A float in the range [0.0-1.0].
    """
    def srgb_to_linear(c: float) -> float:
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = average_rgb(image)

    R = srgb_to_linear(r)
    G = srgb_to_linear(g)
    B = srgb_to_linear(b)

    y = 0.2126 * R + 0.7152 * G + 0.0722 * B
    logger.debug("Relative luminance: %.4f", y)
    return y


def brightness_hsp(image: Image.Image) -> float:
    """
    Estimate perceived image brightness using the HSP color model.

    The HSP (Hue, Saturation, Perceived brightness) model computes
    brightness using squared RGB values, which better matches how humans
    perceive changes in intensity.

    Compared to simple luminance formulas, this emphasizes strong colors
    and highlights more clearly.

    Conceptually, this answers:
        "How intense or vivid does the image feel?"

    Returns:
        A brightness value in the range [0-255].
    """
    r, g, b = average_rgb(image)
    brightness = math.sqrt(
        0.299 * r * r +
        0.587 * g * g +
        0.114 * b * b
    )
    logger.debug("HSP brightness: %.3f", brightness)
    return brightness


def colorfulness(image: Image.Image) -> float:
    """
    Measure how colorful an image appears.

    This uses the Hasler–Süsstrunk colorfulness metric, which estimates
    how strongly colors differ from gray and from each other.

    Images with many vivid, distinct colors score high.
    Images that are grayscale, muted, or monotone score low.

    Conceptually, this answers:
        "How rich or vibrant are the colors in this image?"

    Returns:
        A non-negative float. Higher values indicate more colorfulness.
    """
    image = _validate_image(image)
    arr = np.asarray(image.convert("RGB"), dtype=np.float32)

    R, G, B = arr[..., 0], arr[..., 1], arr[..., 2]

    rg = R - G
    yb = 0.5 * (R + G) - B

    std_rg = rg.std()
    std_yb = yb.std()
    mean_rg = rg.mean()
    mean_yb = yb.mean()

    value = math.sqrt(std_rg**2 + std_yb**2) + 0.3 * math.sqrt(mean_rg**2 + mean_yb**2)

    logger.debug("Colorfulness: %.3f", value)
    return float(value)


def rms_contrast(image: Image.Image) -> float:
    """
    Measure overall contrast in an image using RMS (root-mean-square).

    RMS contrast measures how much pixel intensities vary from the
    average brightness of the image.

    Images with strong light-dark variation have high contrast.
    Flat or foggy images have low contrast.

    Conceptually, this answers:
        "How much do light and dark regions differ overall?"

    Returns:
        A non-negative float. Higher values indicate stronger contrast.
    """
    image = _validate_image(image)
    arr = np.asarray(image.convert("L"), dtype=np.float32)

    mean = arr.mean()
    contrast = math.sqrt(((arr - mean) ** 2).mean())

    logger.debug("RMS contrast: %.3f", contrast)
    return float(contrast)


def rgb_histograms(image: Image.Image):
    """
    Compute per-channel color histograms for an image.

    A histogram counts how many pixels fall into each possible
    intensity value (0–255) for the red, green, and blue channels.

    Conceptually, this answers:
        "How are color intensities distributed in this image?"

    Returns:
        Three lists of length 256:
            (red_hist, green_hist, blue_hist)
    """
    image = _validate_image(image)
    r, g, b = image.convert("RGB").split()
    return r.histogram(), g.histogram(), b.histogram()


def analyze_image(image: Image.Image) -> dict:
    """
    Compute a collection of useful image statistics.

    This is a convenience function that aggregates several commonly
    used color and brightness metrics into a single result.

    Returns:
        A dictionary containing:
            - average RGB color
            - perceived luminance
            - relative luminance
            - brightness
            - colorfulness
            - contrast
    """
    image = _validate_image(image)
    return {
        "average_rgb": average_rgb(image),
        "luminance_bt709": luminance_bt709(image),
        "relative_luminance": relative_luminance(image),
        "brightness_hsp": brightness_hsp(image),
        "colorfulness": colorfulness(image),
        "rms_contrast": rms_contrast(image),
    }


def crop_image(image: Image.Image, left: int, top: int, right: int, bottom: int) -> Image.Image:
    """
    Crop an image to a rectangular region.

    This removes everything outside a bounding box,
    keeping only the specified rectangle.

    Args:
        image: A PIL Image to crop.
        left, top: Coordinates of the top-left corner of the crop box.
        right, bottom: Coordinates of the bottom-right corner of the crop box.

    Returns:
        A new PIL Image containing only the cropped region.
    """
    image = _validate_image(image)
    return image.crop((left, top, right, bottom))


def quantize_kmeans(
    image: Image.Image,
    k: int = 8,
    iterations: int = 10
) -> Image.Image:
    """
    Reduce the number of colors in an image using k-means clustering.

    Color quantization is the process of approximating the original
    colors using a limited set of representative colors.
    This is useful for:
        - Reducing file size
        - Creating color palettes
        - Stylized or posterized effects

    Args:
        image: A PIL Image to quantize.
        k: Number of colors to reduce the image to (default 8).
        iterations: Number of k-means iterations for refining clusters (default 10).

    Returns:
        A new RGB PIL Image where all pixels are replaced by the
        nearest of k representative colors.
    """
    image = _validate_image(image)

    if k <= 0:
        raise ValueError("k must be > 0")
    if iterations <= 0:
        raise ValueError("iterations must be > 0")

    img = image.convert("RGB")
    pixels = np.asarray(img, dtype=np.float32).reshape(-1, 3)

    if len(pixels) < k:
        raise ValueError("k cannot exceed number of pixels")

    centers = pixels[np.random.choice(len(pixels), k, replace=False)]

    for _ in range(iterations):
        distances = np.linalg.norm(pixels[:, None] - centers[None, :], axis=2)
        labels = distances.argmin(axis=1)

        for i in range(k):
            mask = labels == i
            if mask.any():
                centers[i] = pixels[mask].mean(axis=0)

    quantized = centers[labels].astype(np.uint8)
    out = Image.fromarray(quantized.reshape(img.size[1], img.size[0], 3), "RGB")

    logger.debug("Quantized image to %d colors", k)
    return out


def preview_image(image: Image.Image, title: str = "Image Preview") -> None:
    """
    Open a preview window to display a PIL Image.

    Args:
        image: A PIL.Image.Image object to display.
        title: Optional window title.
    """
    if not isinstance(image, Image.Image):
        raise TypeError("image must be a PIL.Image.Image instance")

    # Create main Tkinter window
    root = tk.Tk()
    root.title(title)

    # Convert PIL Image to Tkinter format
    tk_image = ImageTk.PhotoImage(image)

    # Create label and pack image
    label = tk.Label(root, image=tk_image)
    label.pack()

    # Ensure the window closes properly
    def on_close():
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    # Start Tkinter event loop
    root.mainloop()
