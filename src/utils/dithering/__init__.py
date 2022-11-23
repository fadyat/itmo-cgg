import enum


class DitheringAlgo(enum.Enum):
    NONE = 1
    RANDOM = 2
    ORDERED_8X8 = 3
    FLOYD_STEINBERG = 4
    ATKINSON = 5


def apply_dithering(
    algo: DitheringAlgo,
    content: list[float],
):
    ...
