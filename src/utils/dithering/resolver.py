import enum

from src.entities.pnm import PnmFileUI
from src.utils.dithering.ordered import ordered_pixel
from src.utils.dithering.random import random_pixel


class DitheringAlgo(enum.Enum):
    NONE = 0
    RANDOM = 1
    ORDERED_8X8 = 2
    FLOYD_STEINBERG = 3
    ATKINSON = 4


def apply_dithering(
    algo: DitheringAlgo,
    img: PnmFileUI,
    pos: int,
    disabled_channels: list[bool],
):
    if algo == DitheringAlgo.NONE:
        return img.get_px(pos, disabled_channels)

    if algo == DitheringAlgo.RANDOM:
        return random_pixel(img.get_px(pos, disabled_channels))

    if algo == DitheringAlgo.ORDERED_8X8:
        return ordered_pixel(img.get_px(pos, disabled_channels), img.get_x(pos), img.get_y(pos))

    ...
