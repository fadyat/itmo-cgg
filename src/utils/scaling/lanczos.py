import math

from src.entities.pnm import PnmFileUI


def lanczos_scaling(
    img: PnmFileUI,
    new_width: int,
    new_height: int,
):
    x_ratio, y_ratio = img.width / new_width, img.height / new_height

    x_scaled = []
    for i in range(0, img.get_size(), img.width):
        row_values = img.content[i: i + img.width]
        for j in range(new_width):
            scaled = lanczos_point(j * x_ratio, row_values)
            x_scaled.append(scaled)

    new_content = [0] * new_height * new_width
    for col_idx in range(new_width):
        column_values = x_scaled[col_idx::new_width]
        for j in range(new_height):
            scaled = lanczos_point(j * y_ratio, column_values)
            new_content[col_idx + j * new_width] = scaled

    return PnmFileUI(
        pnm_format=img.pnm_format,
        width=new_width,
        height=new_height,
        max_color=img.max_color,
        bytes_per_px=img.bytes_per_px,
        content=new_content,
    )


def lanczos_point(
    x: float,
    values: list[float],
    a: int = 3,
):
    lower_bound = math.floor(x) - a + 1
    upper_bound = math.floor(x) + a

    return sum(
        values[clamp(i, len(values) - 1)] * lanczos_kernel(x - i, a)
        for i in range(lower_bound, upper_bound + 1)
    )


def lanczos_kernel(
    x: float,
    a: float,
):
    if x == 0:
        return 1

    if abs(x) > a:
        return 0

    return (a * math.sin(math.pi * x) * math.sin(math.pi * x / a)) / (math.pi * math.pi * x * x)


def clamp(
    x: int,
    right_limit: int,
) -> int:
    return max(0, min(x, right_limit))


if __name__ == '__main__':
    lanczos_scaling(
        PnmFileUI(
            width=3, height=3, bytes_per_px=1, pnm_format=None,
            content=[6, 2, 4, 1, 9, 5, 3, 0, 7], max_color=255
        ), 4, 2,
    )
