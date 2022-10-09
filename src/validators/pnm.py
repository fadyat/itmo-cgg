import typing

from src import config, typedef
from src.errors.pnm import PnmHeaderError, PnmError


def validate_max_color(
    max_color_value: str | typedef.color_code,
) -> int:
    try:
        max_color_value = int(max_color_value)
    except ValueError:
        raise PnmHeaderError('Invalid max color value %s' % max_color_value)

    if max_color_value > 255:
        raise PnmHeaderError('Max color value %s is too big' % max_color_value)

    return max_color_value


def validate_width_and_height(
    file_size: str | typing.Tuple[int, int],
) -> typing.Tuple[int, int]:
    try:
        if isinstance(file_size, str):
            width, height = tuple(map(int, file_size.split(' ')))
        else:
            width, height = file_size
    except ValueError:
        raise PnmHeaderError('Invalid file size %s' % file_size)

    return width, height


def validate_pnm_format(
    pnm_format: str,
    supported_formats: typing.Tuple[str, ...] = config.PNM_SUPPORTED_FORMATS,
):
    if pnm_format not in supported_formats:
        raise PnmHeaderError('Unsupported format %s' % pnm_format)

    return pnm_format


def validate_file(
    file: typing.BinaryIO,
):
    if file.closed:
        raise PnmError('File is closed, use context manager')


def validate_image_content(
    image_content: typing.Tuple[typedef.color_code],
    width: int,
    height: int,
    bytes_per_pixel: int,
):
    if len(image_content) // width != bytes_per_pixel * height:
        raise PnmError('Invalid image content size')

    return image_content
