import typing

from src import config
from src.errors.pnm import PnmError, PnmColorError, PnmSizeError, PnmFormatError


def validate_color_value(
    color_value: int,
    max_color_value: int,
):
    if color_value > max_color_value:
        raise PnmColorError('Color value "%s" is too big' % color_value)


def validate_max_color(
    max_color_value: typing.Union[str, int],
) -> int:
    try:
        max_color_value = int(max_color_value)
    except ValueError:
        raise PnmColorError('Invalid max color value "%s"' % max_color_value)

    if max_color_value > 255:
        raise PnmColorError('Max color value "%s" is too big' % max_color_value)

    if max_color_value < 0:
        raise PnmColorError('Max color value "%s" is too small' % max_color_value)

    return max_color_value


def validate_width_and_height(
    file_size: typing.Union[str, typing.Tuple[int, int]],
) -> typing.Tuple[int, int]:
    try:
        if isinstance(file_size, str):
            width, height = tuple(map(int, file_size.split(' ')))
        else:
            width, height = file_size
    except ValueError:
        raise PnmSizeError('Invalid file size "%s"' % file_size)

    if width <= 0 or height <= 0:
        raise PnmSizeError('Invalid file size "%s"' % file_size)

    return width, height


def validate_pnm_format(
    pnm_format: str,
    supported_formats: typing.Tuple[str, ...] = config.PNM_SUPPORTED_FORMATS,
):
    if pnm_format not in supported_formats:
        raise PnmFormatError('Unsupported format "%s"' % pnm_format)

    return pnm_format


def validate_file(
    file: typing.BinaryIO,
):
    if file.closed:
        raise PnmError('File is closed, use context manager')


def validate_image_content(
    image_content: typing.Sequence[int],
    width: int,
    height: int,
    pnm_format: str,
):
    validate_pnm_format(pnm_format)
    bytes_per_pixel = config.PNM_BYTES_PER_PIXEL[pnm_format]
    if len(image_content) // width != bytes_per_pixel * height:
        raise PnmSizeError('Invalid image content size')

    return image_content
