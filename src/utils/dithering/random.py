from random import random


def random_dithering(
    content: list[float],
    bytes_per_px: int = 3,
):
    return [
        j for i in range(0, len(content), bytes_per_px)
        for j in random_pixel(content[i], bytes_per_px)
    ]


def random_pixel(
    pixel: float,
    bytes_per_px: int = 3,
) -> list[float]:
    value = random() - 0.5
    color = 0 if value < pixel else 1
    return [color for _ in range(bytes_per_px)]
