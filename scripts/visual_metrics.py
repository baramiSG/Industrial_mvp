from __future__ import annotations

from collections.abc import Sequence
from typing import Any


TOLERANCE = {
    "channel_delta": 8,
    "significant_pixel_ratio": 0.001,
    "mean_absolute_channel_error": 0.20,
}
RGBPixel = tuple[int, int, int]


def calculate_metrics(
    *,
    significant_pixels: int,
    total_pixels: int,
    absolute_channel_error: int,
    dimensions: tuple[int, int],
) -> dict[str, Any]:
    """Apply the single governed visual-tolerance rule."""
    if total_pixels <= 0:
        raise ValueError("image dimensions must contain pixels")
    ratio = significant_pixels / total_pixels
    mean = absolute_channel_error / (total_pixels * 3)
    return {
        "dimensions": list(dimensions),
        "significant_pixels": significant_pixels,
        "total_pixels": total_pixels,
        "significant_pixel_ratio": round(ratio, 6),
        "mean_absolute_channel_error": round(mean, 6),
        "passes": (
            ratio <= TOLERANCE["significant_pixel_ratio"]
            and mean <= TOLERANCE["mean_absolute_channel_error"]
        ),
    }


def compare_pixel_buffers(
    baseline: Sequence[RGBPixel],
    actual: Sequence[RGBPixel],
    *,
    dimensions: tuple[int, int],
) -> dict[str, Any]:
    """Compare small RGB buffers without an image-codec dependency."""
    expected = dimensions[0] * dimensions[1]
    if len(baseline) != expected or len(actual) != expected:
        raise ValueError("pixel buffers do not match image dimensions")
    significant = 0
    channel_error = 0
    for reference, current in zip(baseline, actual, strict=True):
        deltas = tuple(
            abs(reference[index] - current[index])
            for index in range(3)
        )
        channel_error += sum(deltas)
        if max(deltas) > TOLERANCE["channel_delta"]:
            significant += 1
    return calculate_metrics(
        significant_pixels=significant,
        total_pixels=expected,
        absolute_channel_error=channel_error,
        dimensions=dimensions,
    )
