import pytest

from project.module_a.core import addition, subtraction

def test_addition():
    assert addition(60,9) == 69

