import typing
from random import random

from src.utils.dithering import resolve_pixel_dither


def random_pixel(
    pixel: typing.List[float],
    dithering_bits_values: typing.List[float],
) -> list[float]:
    avg, rnd = sum(pixel) / len(pixel), random() - .5
    color = resolve_pixel_dither(avg + rnd, dithering_bits_values)
    return [color, color, color]
