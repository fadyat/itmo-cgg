import math

from src.entities.pnm import PnmFileUI


def lanczos_scaling(
    img: PnmFileUI,
    new_width: int,
    new_height: int,
):
    x_ratio, y_ratio = img.width / new_width, img.height / new_height

    x_scaled = [0] * new_width * img.height * img.bytes_per_px
    for row_idx in range(0, img.get_size(), img.width * img.bytes_per_px):
        for channel in range(img.bytes_per_px):
            begin, end = row_idx + channel, row_idx + img.width * img.bytes_per_px
            channel_row_values = img.content[begin: end: img.bytes_per_px]
            channel_values = [
                lanczos_point(j * x_ratio, channel_row_values)
                for j in range(new_width)
            ]
            for i, val in enumerate(channel_values):
                new_row_idx = row_idx // img.width * new_width
                x_scaled[new_row_idx + i * img.bytes_per_px + channel] = val

    new_content = [0] * new_height * new_width * img.bytes_per_px
    for col_idx in range(0, new_width * img.bytes_per_px, img.bytes_per_px):
        for channel in range(img.bytes_per_px):
            channel_column_values = x_scaled[col_idx + channel::new_width * img.bytes_per_px]
            for row_idx in range(new_height):
                scaled = lanczos_point(row_idx * y_ratio, channel_column_values)
                new_content[col_idx + row_idx * new_width * img.bytes_per_px + channel] = scaled

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
