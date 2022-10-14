import pytest

from src.errors.pnm import PnmError
from src.files.pnm import PnmIO


def test_put_invalid_file_path():
    invalid_file_path = "INVALID_FILE_PATH"
    with pytest.raises(PnmError):
        with PnmIO(image_path=invalid_file_path):
            pass


def test_wrong_file_header_size(invalid_pnm_file_name):
    with PnmIO(invalid_pnm_file_name) as pnm_file:
        with pytest.raises(PnmError):
            pnm_file.read()
