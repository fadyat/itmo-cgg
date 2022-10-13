import tempfile

import pytest


@pytest.fixture()
def file():
    with tempfile.NamedTemporaryFile() as file:
        yield file


