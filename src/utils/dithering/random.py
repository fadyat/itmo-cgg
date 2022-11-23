import typing
from random import random


def random_pixel(
    pixel: typing.List[float],
) -> list[float]:
    avg = sum(pixel) / len(pixel)
    color = 0 if random() >= avg else 1
    return [color, color, color]
