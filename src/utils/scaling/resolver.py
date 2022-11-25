import enum


class ScalingAlgo(enum.Enum):
    NONE = 0
    NEAREST_NEIGHBOR = 1
    BILINEAR = 2
    LANCZOS3 = 3
    BC_SPLINE = 4


def apply_scaling(
    algo: ScalingAlgo,
):
    ...
