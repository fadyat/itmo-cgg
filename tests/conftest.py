import tempfile

import pytest

pytest_plugins = [
    "tests.fixtures.pnm",
]


@pytest.fixture
def file():
    with tempfile.NamedTemporaryFile() as file:
        yield file
