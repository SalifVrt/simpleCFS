"""Test configuration file to handle paths to test files."""

import pytest
import os

@pytest.fixture
def fpath(file="td1.txt"):
    """
    Returns absolute path to file.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "testfiles", file)
    return file_path