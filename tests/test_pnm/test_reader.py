import pytest

from src.errors.pnm import PnmError, PnmSizeError, PnmFormatError, PnmColorError
from src.files.pnm import PnmIO


def test_wrong_file_path():
    invalid_file_path = "INVALID_FILE_PATH"
    with pytest.raises(PnmError):
        with PnmIO(image_path=invalid_file_path):
            ...


def test_wrong_format(
    pnm_file_wrong_format,
):
    with PnmIO(pnm_file_wrong_format) as r:
        with pytest.raises(PnmFormatError):
            r.read()


def test_wrong_max_color_value(
    pnm_file_wrong_max_color_value,
):
    with PnmIO(pnm_file_wrong_max_color_value) as r:
        with pytest.raises(PnmColorError):
            r.read()


def test_wrong_content_size(
    pnm_file_content_size_not_enough,
    pnm_file_content_size_too_much,
):
    with PnmIO(pnm_file_content_size_not_enough) as r:
        with pytest.raises(PnmSizeError):
            r.read()

    with PnmIO(pnm_file_content_size_too_much) as r:
        with pytest.raises(PnmSizeError):
            r.read()


def test_valid_file_read(
    valid_pnm_file_total,
):
    file_path, expected_pnm_file = valid_pnm_file_total
    with PnmIO(file_path) as r:
        pnm_file = r.read()

    assert pnm_file.pnm_format == expected_pnm_file.pnm_format
    assert pnm_file.width == expected_pnm_file.width
    assert pnm_file.height == expected_pnm_file.height
    assert pnm_file.max_color == expected_pnm_file.max_color
    assert pnm_file.bytes_per_pixel == expected_pnm_file.bytes_per_pixel
    assert pnm_file.content == expected_pnm_file.content


def test_valid_file_read_ui(
    valid_pnm_file_total_ui,
):
    pytest.skip("Deprecated")

    file_path, expected_pnm_file = valid_pnm_file_total_ui
    with PnmIO(file_path) as r:
        pnm_file = r.read_for_ui()

    assert pnm_file.pnm_format == expected_pnm_file.pnm_format
    assert pnm_file.width == expected_pnm_file.width
    assert pnm_file.height == expected_pnm_file.height
    assert pnm_file.max_color == expected_pnm_file.max_color
    assert pnm_file.bytes_per_px == expected_pnm_file.bytes_per_px
    assert tuple(pnm_file.content) == tuple(expected_pnm_file.content)
