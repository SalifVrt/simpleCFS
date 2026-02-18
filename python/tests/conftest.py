"""Test configuration file to handle paths to test files."""

import pytest
import os

@pytest.fixture
def td1_path():
    """
    Returns absolute path to td1.txt.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "testfiles", "td1.txt")
    return file_path