import typing

import pytest

from src.entities.pnm import PnmFile, PnmFileUI
from src.files.pnm import PnmIO


@pytest.fixture
def valid_pnm_file_total(file) -> typing.Tuple[str, PnmFile]:
    content = [2 for _ in range(2 ** 2)]
    p = PnmFile().create(
        pnm_format="P5",
        width=2,
        height=2,
        max_color=255,
        bytes_per_pixel=1,
        content=bytes(content),
    )

    with PnmIO(file.name, 'wb') as pnm_file:
        pnm_file.write(
            pnm_format=p.pnm_format,
            width=p.width,
            height=p.height,
            image_content=content,
        )

    yield file.name, p


@pytest.fixture
def valid_pnm_file_total_ui(file) -> typing.Tuple[str, PnmFileUI]:
    content = [2 for _ in range(2 ** 2)]
    p = PnmFileUI(
        pnm_format="P5",
        width=2,
        height=2,
        max_color=255,
        bytes_per_pixel=1,
        content=content,
    )

    with PnmIO(file.name, 'wb') as pnm_file:
        pnm_file.write(
            pnm_format=p.pnm_format,
            width=p.width,
            height=p.height,
            image_content=content,
        )

    yield file.name, p


@pytest.fixture
def pnm_file_content_size_not_enough(file):
    with open(file.name, 'wb') as f:
        f.write(b'P5\n2 2\n255\n\x00')

    yield file.name


@pytest.fixture
def pnm_file_content_size_too_much(file):
    with open(file.name, 'wb') as f:
        f.write(b'P5\n2 2\n255\n\x00\x00\x00\x00\x00\x00')

    yield file.name


@pytest.fixture
def pnm_file_wrong_format(file):
    with open(file.name, 'wb') as f:
        f.write(b'P4\n2 2\n255\n\x00')

    yield file.name


@pytest.fixture
def pnm_file_wrong_max_color_value(file):
    with open(file.name, 'wb') as f:
        f.write(b'P5\n2 2\n256\n\x00')

    yield file.name
