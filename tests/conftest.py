import tempfile

import pytest

from src.files.pnm import PnmFile


@pytest.fixture()
def file():
    with tempfile.NamedTemporaryFile() as file:
        yield file


@pytest.fixture()
def valid_pnm_file_name(file):
    with PnmFile(file.name, 'wb') as pnm_file:
        arr = [2 for _ in range(200 ** 2)]
        pnm_file.write("P5", 200, 200, arr)
    yield file.name


@pytest.fixture()
def invalid_pnm_file_name(file):
    with open(file.name, 'wb') as f:
        s = b"P5\n2 2\n255\n"
        s += b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        f.write(s)
    yield file.name
