import typing
from random import uniform

from src.utils.dithering import find_closest_px


def random_pixel(
    pixel: typing.List[float],
    dithering_bits_values: typing.List[float],
) -> list[float]:
    avg = sum(pixel) / len(pixel)
    rnd = uniform(-1 / len(dithering_bits_values), 1 / len(dithering_bits_values))
    color = find_closest_px(avg + rnd, dithering_bits_values)
    return [color, color, color]
