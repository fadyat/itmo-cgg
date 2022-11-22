from random import random, randint


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


def random_pixel_byte(
    pixel: int,
    bytes_per_px: int = 3,
) -> list[int]:
    color = 0 if randint(0, 255) >= pixel else 255
    return [color for _ in range(bytes_per_px)]


def random_dithering_bytes(
    content: list[int],
    bytes_per_px: int = 3,
):
    return [
        j for i in range(0, len(content), bytes_per_px)
        for j in random_pixel_byte(content[i], bytes_per_px)
    ]
