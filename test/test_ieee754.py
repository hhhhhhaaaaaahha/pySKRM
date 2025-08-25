import math
import pytest

try:
    from pyskrm.ieee754 import convert_float_to_ieee754_single, flip_ieee754
except Exception:  # pragma: no cover
    from ieee754 import convert_float_to_ieee754_single, flip_ieee754


@pytest.mark.parametrize(
    "number,expected_bits",
    [
        # 32-bit IEEE754: 0x00000000, 0x3f800000, 0xbf800000, 0x3f000000
        (0.0, "0" * 32),
        (1.0, "00111111100000000000000000000000"),
        (-1.0, "10111111100000000000000000000000"),
        (0.5, "00111111000000000000000000000000"),
    ],
)
def test_convert_float_to_ieee754_single_basic(number, expected_bits):
    bits = convert_float_to_ieee754_single(number)
    assert isinstance(bits, str)
    assert len(bits) == 32
    assert bits == expected_bits


@pytest.mark.parametrize("number", [0.0, 1.0, -1.0, 0.5, 2.5, 123.456])
def test_convert_is_deterministic_and_32bits(number):
    a = convert_float_to_ieee754_single(number)
    b = convert_float_to_ieee754_single(number)
    assert a == b
    assert len(a) == 32
    assert set(a) <= {"0", "1"}


def test_flip_ieee754_contract_when_flip_bit_false():
    # flip_bit=False should return a 32-bit string
    bits = convert_float_to_ieee754_single(1.0, flip_bit=False)
    assert len(bits) == 32
    assert bits.startswith(("0", "1"))


@pytest.mark.parametrize(
    "number,expect_leading,should_flip",
    [
        # flip_ieee754: if # of 1's > 16, return "1" + (bitwise-not)
        # else return "0" + original string
        # The length should be both 33
        (0.0, "0", False),
        (1.0, "0", False),       # 1-count of 1.0 = 7
        (-1.0, "0", False),      # 1-count of -1.0 = 8
        (0.5, "0", False),       # 1-count of 0.5 = 6
        (123.456, "1", True),    # 1-count = 18 (>16)，should be flipped
    ],
)
def test_flip_ieee754_behavior(number, expect_leading, should_flip):
    orig = convert_float_to_ieee754_single(number)
    flipped = flip_ieee754(orig)  # Test the action of self-defined function
    assert len(flipped) == 33
    assert flipped[0] == expect_leading

    if should_flip:
        # Except for leading bit，other bits should be bitwise-not
        body = flipped[1:]
        assert body == orig.translate(str.maketrans("01", "10"))
    else:
        # Should be leading '0' + original string
        assert flipped[1:] == orig


def test_convert_with_flip_bit_true_is_33bits_and_consistent():
    orig = convert_float_to_ieee754_single(123.456, flip_bit=False)
    with_flip = convert_float_to_ieee754_single(123.456, flip_bit=True)
    assert len(with_flip) == 33
    # flip_bit=True = flip_ieee754
    assert with_flip == flip_ieee754(orig)
