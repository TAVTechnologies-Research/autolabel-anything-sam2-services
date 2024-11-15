import cv2 as cv
import numpy as np

from typing import List, Optional

MIN_POLYGON_POINT_COUNT = 3


def mask_to_polygons(mask: np.ndarray, normalized: bool = False) -> List[np.ndarray]:
    """
    Converts a binary mask to a list of polygons.

    Parameters:
        mask (np.ndarray): A binary mask represented as a 2D NumPy array of
            shape `(H, W)`, where H and W are the height and width of
            the mask, respectively.
        normalized (bool): If `True`, the polygon coordinates are normalized

    Returns:
        List[np.ndarray]: A list of polygons, where each polygon is represented by a
            NumPy array of shape `(N, 2)`, containing the `x`, `y` coordinates
            of the points. Polygons with fewer points than `MIN_POLYGON_POINT_COUNT = 3`
            are excluded from the output.
    """

    contours, _ = cv.findContours(
        mask.astype(np.uint8), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE
    )

    polygons = [
        np.squeeze(contour, axis=1)
        for contour in contours
        if contour.shape[0] >= MIN_POLYGON_POINT_COUNT
    ]

    if normalized:
        polygons = [
            polygon / np.array([mask.shape[1], mask.shape[0]]) for polygon in polygons
        ]
    return polygons


def mask_to_xyxy(masks: np.ndarray, normlized: bool = False) -> np.ndarray:
    """
    Converts a 3D `np.array` of 2D bool masks into a 2D `np.array` of bounding boxes.

    Parameters:
        masks (np.ndarray): A 3D `np.array` of shape `(N, W, H)`
            containing 2D bool masks
        normalized (bool): If `True`, the bounding box coordinates are normalized
            to the range `[0, 1]`. Default is `False`.

    Returns:
        np.ndarray: A 2D `np.array` of shape `(N, 4)` containing the bounding boxes
            `(x_min, y_min, x_max, y_max)` for each mask
    """
    n = masks.shape[0]
    xyxy = np.zeros((n, 4), dtype=np.float32)

    for i, mask in enumerate(masks):
        rows, cols = np.where(mask)

        if len(rows) > 0 and len(cols) > 0:
            x_min, x_max = np.min(cols), np.max(cols)
            y_min, y_max = np.min(rows), np.max(rows)
            xyxy[i, :] = [x_min, y_min, x_max, y_max]
            if normlized:
                xyxy[i, :] = xyxy[i, :] / np.array([mask.shape[1], mask.shape[0]] * 2)
    return xyxy.astype(np.int64) if not normlized else xyxy
