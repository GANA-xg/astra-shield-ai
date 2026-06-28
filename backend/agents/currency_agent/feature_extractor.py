"""
Feature extraction module for the Currency Detection Agent.

This module extracts basic visual information from a currency note.
"""

from pathlib import Path
import cv2
import numpy as np


def load_image(image_path: str) -> np.ndarray:
    """
    Load an image from disk.

    Args:
        image_path: Path to the image.

    Returns:
        OpenCV image.

    Raises:
        FileNotFoundError:
            If image does not exist.

        ValueError:
            If image cannot be opened.
    """

    image_file = Path(image_path)

    if not image_file.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    image = cv2.imread(str(image_file))

    if image is None:
        raise ValueError(
            "Unable to read image."
        )

    return image


def preprocess_image(image: np.ndarray) -> dict:
    """
    Convert the image into different color spaces
    needed for feature extraction.

    Args:
        image: Original BGR image.

    Returns:
        Dictionary containing processed images.
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    return {
        "original": image,
        "gray": gray,
        "hsv": hsv,
    }


def calculate_sharpness(gray_image: np.ndarray) -> dict:
    """
    Measure image sharpness using the
    Variance of the Laplacian.

    Args:
        gray_image: Grayscale image.

    Returns:
        Dictionary containing sharpness information.
    """

    score = cv2.Laplacian(
        gray_image,
        cv2.CV_64F
    ).var()

    return {
        "sharpness_score": float(score),
        "is_sharp": bool(score > 100)
     }


def detect_security_thread(gray_image: np.ndarray) -> dict:
    """
    Detect possible security thread using edge detection
    and Hough Line Transform.
    """

    # Detect edges
    edges = cv2.Canny(
        gray_image,
        50,
        150,
    )

    # Detect lines
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=100,
        minLineLength=120,
        maxLineGap=15,
    )

    vertical_lines = []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]

            # Keep almost vertical lines only
            if abs(x1 - x2) < 10:
                vertical_lines.append(
                    (x1, y1, x2, y2)
                )

    return {
        "detected": len(vertical_lines) > 0,
        "line_count": len(vertical_lines),
        "lines": vertical_lines,
        "edges": edges,
    }





def extract_features(image_path: str) -> dict:
    """
    Complete feature extraction pipeline.

    Args:
        image_path: Path to the currency image.

    Returns:
        Dictionary containing extracted features.
    """

    image = load_image(image_path)

    processed = preprocess_image(image)

    sharpness = calculate_sharpness(
        processed["gray"]
    )

    security_thread = detect_security_thread(
        processed["gray"]
    )

    save_debug_edges(
        security_thread["edges"]
    )

    return {
        "sharpness": sharpness,
        "security_thread": {
            "detected": security_thread["detected"],
            "line_count": security_thread["line_count"],
        },
    }



def save_debug_edges(edges: np.ndarray) -> None:
    """
    Save detected edges for debugging.
    """

    debug_dir = Path(__file__).parent / "debug"

    debug_dir.mkdir(
        exist_ok=True
    )

    cv2.imwrite(
        str(debug_dir / "edges.jpg"),
        edges,
    )