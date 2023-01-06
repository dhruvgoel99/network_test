""" Test example for fixture and parameterize """
import random
import pytest


@pytest.fixture
def generate_num():
    """ Generate random values with spacing of 2 """
    res = [random.randrange(2, 50, 2) for i in range(5)]
    return res


@pytest.fixture
def generate_odd():
    """ Generate random values """
    res = [random.randrange(1, 50) for i in range(5)]
    return res


def test_even_val(generate_num):
    # pylint: disable=redefined-outer-name
    """ Test for even values from random values
        with spacing of 2 """
    test = [1 if i % 2 == 0 else 0 for i in generate_num]
    assert sum(test) == len(generate_num)


def test_rand_val(generate_odd):
    # pylint: disable=redefined-outer-name
    """ Test for even values from random values """
    test = [1 if i % 2 == 0 else 0 for i in generate_odd]
    assert sum(test) == len(generate_odd)


@pytest.mark.parametrize("num", [10, 20, 11, 15])
def test_multiplication_11(num):
    """ Test for divisibility by 5 """
    assert num % 5 == 0
