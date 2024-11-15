import io
import base64
from typing import Tuple, List, Optional, Dict

import cv2 as cv
import numpy as np
from PIL import Image


def hex_to_rgb(hex: str) -> Tuple[int, ...]:
    """Converts a hex color string to an RGB tuple.

    Args:
        hex (str): Hex color string

    Returns:
        Tuple[int, ...]: rgb tuple
    """
    hex = hex.lstrip("#").upper()
    return tuple(int(hex[i : i + 2], 16) for i in (0, 2, 4))


def image_to_base64(src_image: np.ndarray, encode: bool = False) -> str:
    """Convert image to base64

    Args:
        image (np.ndarray): image

    Returns:
        str: base64 encoded image
    """
    if not encode:
        image = Image.fromarray(src_image)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    else:
        encode_param = [int(cv.IMWRITE_JPEG_QUALITY), 70]
        result, encimg = cv.imencode(".jpg", src_image, encode_param)
        return base64.b64encode(encimg).decode("utf-8")  # type: ignore


def draw_masks_on_image(
    src_image: np.ndarray, masks: Dict[str, np.ndarray], color: Dict[str, str]
) -> np.ndarray:
    """Draws segmentation masks on the source image.

    Args:
        src_image (np.ndarray): original image in [HxWx3] format (pixel values in [0, 255])
        masks (Dict[str, np.ndarray]): Dict of masks object_id -> mask
        color (Dict[str, str]): Dict of colors object_id -> color(hex)

    Returns:
        np.ndarray: Drawn image with masks
    """
    alpha = 0.5
    for obj_id, mask in masks.items():
        obj_color = color.get(obj_id)
        if obj_color is None:
            obj_color = np.random.randint(0, 255, 3).astype(np.uint8)
        else:
            obj_color = hex_to_rgb(obj_color)
            obj_color = np.array(obj_color, dtype=np.uint8)

        if mask.dtype != bool:
            mask = mask.astype(bool)

        overlay = np.zeros_like(src_image)
        overlay[mask] = obj_color

        # perform alpha blending
        blended = src_image.copy().astype(np.float32)
        overlay = overlay.astype(np.float32)

        blended[mask] = (1 - alpha) * blended[mask] + alpha * overlay[mask]

        src_image = blended.astype(np.uint8)

    return src_image
