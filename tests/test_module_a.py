import pytest

from project.module_a.core import addition, subtraction

def test_addition():
    assert addition(60,9) == 69

def test_subtraction():
    assert subtraction(42069, 42000) == 69420
