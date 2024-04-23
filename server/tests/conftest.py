from typing import Any
import pytest
from pathlib import Path
import shutil
import os

from fixtures import *


@pytest.fixture()
def testdir(request: Any) -> Path:
    filename = request.module.__file__
    return Path(filename).parent

'''
@pytest.fixture()
def datadir(tmpdir, request):
    # https://stackoverflow.com/questions/29627341/pytest-where-to-store-expected-data
    filename = request.module.__file__
    testdir, _ = os.path.splitext(filename)
    assert os.path.exists(testdir), f'{test_dir} for canonical results should exists. Please, Create it manually.'

    res = tmpdir / 'data'
    # raise ValueError(str([res, testdir]))

    if os.path.isdir(testdir):
        shutil.copytree(testdir, res)

    return res
'''
