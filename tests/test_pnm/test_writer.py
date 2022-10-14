import pytest

from src.errors.pnm import PnmError, PnmSizeError, PnmFormatError, PnmColorError
from src.files.pnm import PnmIO


@pytest.mark.parametrize(
    'pnm_format, width, height, max_color_value, content',
    [
        ('P5', 1, 1, 1, (0,)),
        ('P6', 1, 1, 1, (0, 0, 0)),
    ],
)
def test_incorrect_file_open(
    pnm_format,
    width,
    height,
    max_color_value,
    content,
    file,
):
    pnm_file = PnmIO(file.name)

    with pytest.raises(PnmError):
        pnm_file.write(
            pnm_format=pnm_format,
            width=width,
            height=height,
            max_color_value=max_color_value,
            image_content=content,
        )


@pytest.mark.parametrize(
    'pnm_format, width, height, max_color_value, content',
    [
        (
            'P5',
            1,
            1,
            1,
            (
                0,
                0,
                0,
            ),
        ),
        ('P6', 1, 1, 1, (0, 0, 0, 0, 0, 0)),
    ],
)
def test_invalid_image_content_size(
    pnm_format,
    width,
    height,
    max_color_value,
    content,
    file,
):
    with PnmIO(file.name, 'wb') as w:
        with pytest.raises(PnmSizeError):
            w.write(
                pnm_format=pnm_format,
                width=width,
                height=height,
                max_color_value=max_color_value,
                image_content=content,
            )


@pytest.mark.parametrize(
    'pnm_format, width, height, max_color_value, content',
    [
        ('P2', 1, 1, 1, (0,)),
        (
            'QQ',
            1,
            1,
            1,
            (
                0,
                0,
                0,
            ),
        ),
    ],
)
def test_invalid_image_format(
    pnm_format,
    width,
    height,
    max_color_value,
    content,
    file,
):
    with PnmIO(file.name, 'wb') as w:
        with pytest.raises(PnmFormatError):
            w.write(
                pnm_format=pnm_format,
                width=width,
                height=height,
                max_color_value=max_color_value,
                image_content=content,
            )


@pytest.mark.parametrize(
    'pnm_format, width, height, max_color_value, content',
    [
        ('P5', 1, 1, 256, (0,)),
        (
            'P6',
            1,
            1,
            -1,
            (
                0,
                0,
                0,
            ),
        ),
    ],
)
def test_invalid_image_max_color_value(
    pnm_format,
    width,
    height,
    max_color_value,
    content,
    file,
):
    with PnmIO(file.name, 'wb') as w:
        with pytest.raises(PnmColorError):
            w.write(
                pnm_format=pnm_format,
                width=width,
                height=height,
                max_color_value=max_color_value,
                image_content=content,
            )


def test_invalid_content_value(file):
    with PnmIO(file.name, 'wb') as w:
        with pytest.raises(PnmColorError):
            w.write(
                pnm_format='P6',
                width=1,
                height=1,
                max_color_value=1,
                image_content=(0, 0, 2),
            )


def test_invalid_image_width(file):
    with PnmIO(file.name, 'wb') as w:
        with pytest.raises(PnmSizeError):
            w.write(
                pnm_format='P6',
                width=-1,
                height=1,
                max_color_value=1,
                image_content=(0, 0, 0),
            )


def test_invalid_image_height(file):
    with PnmIO(file.name, 'wb') as w:
        with pytest.raises(PnmSizeError):
            w.write(
                pnm_format='P6',
                width=1,
                height=-1,
                max_color_value=1,
                image_content=(0, 0, 0),
            )


@pytest.mark.parametrize(
    'pnm_format, width, height, max_color_value, content, expected',
    [
        ('P5', 1, 1, 1, (0,), b'\x00'),
        ('P6', 1, 1, 1, (0, 0, 0), b'\x00\x00\x00'),
        ('P5', 1, 1, 255, (255,), b'\xff'),
        ('P6', 1, 1, 255, (255, 255, 255), b'\xff\xff\xff'),
        ('P5', 2, 3, 255, (0, 255, 0, 255, 0, 255), b'\x00\xff\x00\xff\x00\xff'),
        (
            'P6',
            2,
            3,
            255,
            (0, 0, 0, 255, 255, 255, 0, 0, 0, 255, 255, 255, 0, 0, 0, 255, 255, 255),
            b'\x00\x00\x00\xff\xff\xff\x00\x00\x00\xff\xff\xff\x00\x00\x00\xff\xff\xff',
        ),
        ('P5', 2, 2, 128, (0, 16, 32, 64), b'\x00\x10\x20\x40'),
        (
            'P6',
            2,
            2,
            128,
            (0, 0, 0, 16, 16, 16, 32, 32, 32, 64, 64, 64),
            b'\x00\x00\x00\x10\x10\x10\x20\x20\x20\x40\x40\x40',
        ),
    ],
)
def test_write_file(
    pnm_format,
    width,
    height,
    max_color_value,
    content,
    expected,
    file,
):
    with PnmIO(file.name, 'wb') as w:
        w.write(
            pnm_format=pnm_format,
            width=width,
            height=height,
            max_color_value=max_color_value,
            image_content=content,
        )

    with PnmIO(file.name, 'rb') as r:
        pnm_file = r.read()

    assert pnm_file.pnm_format == pnm_format
    assert pnm_file.width == width
    assert pnm_file.height == height
    assert pnm_file.max_color == max_color_value
    assert pnm_file.bytes_per_pixel == len(content) // (width * height)
    assert pnm_file.bytes_per_pixel == pnm_file.bytes_per_pixel
    assert pnm_file.content == expected
