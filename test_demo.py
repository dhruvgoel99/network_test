""" Test example for fixture and parameterize """
import random
import pytest


@pytest.fixture
def generate_num():
    """ Generate random values with spacing of 2 """
    res = [random.randrange(2, 50, 2) for _ in range(5)]
    return res


@pytest.fixture
def generate_odd():
    """ Generate random values """
    res = [random.randrange(1, 50) for _ in range(5)]
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


class HelperFixt:
    """Helper class for fixture statements """

    def __init__(self, x, y):
        """Constructor to initialize data"""
        self.x = x
        self.y = y

    def command(self):
        """Statement from fixture function"""
        return self.x

    def sec_command(self):
        """Statement for modulus"""
        return self.x % self.y == 0


@pytest.fixture(name="demo_fixt")
def ini_cmd(args):
    """Return fixture results"""
    return HelperFixt(args[0], args[1])


class TestFixtArg:
    """Main class to test fixture arguments"""
    @pytest.mark.parametrize('args', [(10, 2), (20, 2), (30, 2), (55, 2)])
    def test_fixt_arg(self, demo_fixt):
        """Testing function"""
        assert demo_fixt.command() % 2 == 0

    @pytest.mark.parametrize('args', [(10, 2), (20, 5), (30, 6), (55, 11)])
    def test_mod_fix(self, demo_fixt):
        """Test for modulus"""
        assert demo_fixt.sec_command()
