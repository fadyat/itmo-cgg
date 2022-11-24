from src.entities.pnm import PnmFileUI
from src.utils.dithering import find_closest_px


def atkinson_pixel(
    img: PnmFileUI,
    pos: int,
    disabled_channels: list[bool],
    dithering_bits_values: list[float],
):
    px = img.get_px(pos, disabled_channels)
    avg = sum(px) / len(px)
    new_px = find_closest_px(avg, dithering_bits_values)

    img.set_px(pos, [new_px, new_px, new_px])
    error = avg - new_px

    pxs_for_error_diffusion = [
        pos + img.bytes_per_px,
        pos + 2 * img.bytes_per_px,
        pos + img.width * img.bytes_per_px - img.bytes_per_px,
        pos + img.width * img.bytes_per_px,
        pos + img.width * img.bytes_per_px + img.bytes_per_px,
        pos + 2 * img.width * img.bytes_per_px,
    ]

    for px_pos in pxs_for_error_diffusion:
        if px_pos < img.get_size():
            new_value = img.content[px_pos] + error / 8
            img.set_px(px_pos, [new_value, new_value, new_value])

    return img.get_px(pos, disabled_channels)
