import os
import pytest


@pytest.fixture
def tmp_working_dir(tmp_path):
    wd = tmp_path / "workdir"
    wd.mkdir()
    return str(wd)
