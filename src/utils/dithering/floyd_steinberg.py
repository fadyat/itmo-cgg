from src.entities.pnm import PnmFileUI


def floyd_steinberg_pixel(
    img: PnmFileUI,
    pos: int,
    disabled_channels: list[bool],
):
    px = img.get_px(pos, disabled_channels)
    avg = sum(px) / len(px)
    new_px = 0 if avg < 0.5 else 1

    img.set_px(pos, [new_px, new_px, new_px])
    error = avg - new_px

    pxs_for_error_diffusion = [
        (pos + img.bytes_per_px, 7 / 16),
        (pos + img.width * img.bytes_per_px - img.bytes_per_px, 3 / 16),
        (pos + img.width * img.bytes_per_px, 5 / 16),
        (pos + img.width * img.bytes_per_px + img.bytes_per_px, 1 / 16),
    ]

    for px_pos, k in pxs_for_error_diffusion:
        if px_pos < img.get_size():
            new_value = img.content[px_pos] + error * k
            img.set_px(px_pos, [new_value, new_value, new_value])

    return img.get_px(pos, disabled_channels)
