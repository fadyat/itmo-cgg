import math

from src.entities.pnm import PnmFileUI


def bilinear_scaling(
    img: PnmFileUI,
    new_width: int,
    new_height: int,
):
    x_ratio, y_ratio = img.width / new_width, img.height / new_height

    new_content = []
    for i in range(new_height * new_width):
        x_l, y_l = math.floor(i % new_width * x_ratio), math.floor(i // new_width * y_ratio)
        x_h, y_h = math.ceil(i % new_width * x_ratio), math.ceil(i // new_width * y_ratio)
        x_w, y_w = i % new_width * x_ratio - x_l, i // new_width * y_ratio - y_l

        a, b, c, d = 0, 0, 0, 0
        if x_l < img.width and y_l < img.height:
            a = (x_l + y_l * img.width) * img.bytes_per_px

        if x_h < img.width and y_l < img.height:
            b = (x_h + y_l * img.width) * img.bytes_per_px

        if x_l < img.width and y_h < img.height:
            c = (x_l + y_h * img.width) * img.bytes_per_px

        if x_h < img.width and y_h < img.height:
            d = (x_h + y_h * img.width) * img.bytes_per_px

        for channel in range(img.bytes_per_px):
            new_content.append(
                (1 - x_w) * (1 - y_w) * img.content[a + channel]
                + x_w * (1 - y_w) * img.content[b + channel]
                + (1 - x_w) * y_w * img.content[c + channel]
                + x_w * y_w * img.content[d + channel]
            )

    return PnmFileUI(
        pnm_format=img.pnm_format,
        width=new_width,
        height=new_height,
        max_color=img.max_color,
        bytes_per_px=img.bytes_per_px,
        content=new_content,
    )
