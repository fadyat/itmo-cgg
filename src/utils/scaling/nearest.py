from src.entities.pnm import PnmFileUI


def nearest_point_scaling(
    img: PnmFileUI,
    new_width: int,
    new_height: int,
):
    x_ratio, y_ratio = img.width / new_width, img.height / new_height

    new_content = []
    for i in range(new_height * new_width):
        x = int(i % new_width * x_ratio)
        y = int(i // new_width * y_ratio)
        begin = (x + y * img.width) * img.bytes_per_px
        new_content.extend(img.content[begin: begin + img.bytes_per_px])

    return PnmFileUI(
        pnm_format=img.pnm_format,
        width=new_width,
        height=new_height,
        max_color=img.max_color,
        bytes_per_px=img.bytes_per_px,
        content=new_content,
    )
