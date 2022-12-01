import enum

from src.entities.pnm import PnmFileUI
from src.utils.scaling.bilinear import bilinear_scaling
from src.utils.scaling.lanczos import lanczos_scaling
from src.utils.scaling.nearest import nearest_point_scaling


class ScalingAlgo(enum.Enum):
    NONE = 0
    NEAREST_NEIGHBOR = 1
    BILINEAR = 2
    LANCZOS3 = 3
    BC_SPLINE = 4


def apply_scaling(
    algo: ScalingAlgo,
    img: PnmFileUI,
    new_width: int,
    new_height: int,
):
    if img.width == new_width and img.height == new_height:
        return img

    if algo == ScalingAlgo.NONE:
        return img

    if algo == ScalingAlgo.NEAREST_NEIGHBOR:
        return nearest_point_scaling(img, new_width, new_height)

    if algo == ScalingAlgo.BILINEAR:
        return bilinear_scaling(img, new_width, new_height)

    if algo == ScalingAlgo.LANCZOS3:
        return lanczos_scaling(img, new_width, new_height)

    return img
