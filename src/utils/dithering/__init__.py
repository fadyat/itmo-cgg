import typing
from bisect import bisect_left


def resolve_pixel_dither(
    counted_value: float,
    dithering_bits_values: typing.List[float],
) -> float:
    pos = bisect_left(dithering_bits_values, counted_value)

    left = dithering_bits_values[pos - 1] if pos > 0 else 0
    right = dithering_bits_values[pos] if pos < len(dithering_bits_values) else 1

    if counted_value - left < right - counted_value:
        return left

    return right
