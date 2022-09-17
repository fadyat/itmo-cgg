import typing

from src import config
from src.errors.pnm import PnmHeaderError, PnmError


def validate_max_color(
    max_color_value: str,
) -> int:
    try:
        max_color_value = int(max_color_value)
    except ValueError:
        raise PnmHeaderError('Invalid max color value %s' % max_color_value)

    if max_color_value > 255:
        raise PnmHeaderError('Max color value %s is too big' % max_color_value)

    return max_color_value


def validate_width_and_height(
    file_size: str,
) -> typing.Tuple[int, int]:
    try:
        width, height = tuple(map(int, file_size.split(' ')))
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
