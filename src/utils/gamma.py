import enum


class GammaOption(enum.Enum):
    ASSIGN = 0
    CONVERT = 1


def srgb_to_linear(px: list[float]):
    return [
        srgb_channel_to_linear(channel_value)
        for channel_value in px
    ]


def linear_channel_to_srgb(channel_value: float):
    if channel_value <= 0.04045:
        return channel_value / 12.92

    return ((channel_value + 0.055) / 1.055) ** 2.4


def linear_to_srgb(px: list[float]):
    return [
        linear_channel_to_srgb(channel_value)
        for channel_value in px
    ]


def srgb_channel_to_linear(channel_value: float):
    if channel_value <= 0.0031308:
        return channel_value * 12.92

    return 1.055 * (channel_value ** (1 / 2.4)) - 0.055


def to_linear(
    px: list[float],
    gamma: float,
) -> list[float]:
    if gamma == 2.4:
        return srgb_to_linear(px)

    if gamma == 1:
        return px

    return [
        channel_value ** (1 / gamma)
        for channel_value in px
    ]


def from_linear(
    px: list[float],
    gamma: float,
) -> list[float]:
    if gamma == 2.4:
        return linear_to_srgb(px)

    if gamma == 1:
        return px

    return [
        channel_value ** gamma
        for channel_value in px
    ]


def assign_gamma(
    px: list[float],
    prev_gamma: float,
    next_gamma: float,
) -> list[float]:
    if prev_gamma == next_gamma:
        return px

    linear = to_linear(px, prev_gamma)

    return [
        0 if channel_value < 0 else 1 if channel_value > 1 else channel_value
        for channel_value in from_linear(linear, next_gamma)
    ]


def convert_gamma(
    px: list[float],
    prev_gamma: float,
    next_gamma: float,
) -> list[float]:
    if prev_gamma == next_gamma:
        return px

    linear = to_linear(px, prev_gamma)

    recounted = [
        channel_value ** (prev_gamma / next_gamma)
        for channel_value in linear
    ]

    return [
        0 if channel_value < 0 else 1 if channel_value > 1 else channel_value
        for channel_value in from_linear(recounted, next_gamma)
    ]


def resolve_gamma(
    px: list[float],
    prev_gamma: float,
    next_gamma: float,
    gamma_option: GammaOption,
) -> list[float]:
    if gamma_option == GammaOption.ASSIGN:
        return assign_gamma(px, prev_gamma, next_gamma)

    return convert_gamma(px, prev_gamma, next_gamma)
