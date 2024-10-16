from .interface import call_long_shift_right

def test_long_shift_right_one_byte():
    for i in range(256):
        call_long_shift_right(i) == i//2

def test_long_shift_right_two_byte():
    for i in range(2**16):
        call_long_shift_right(i) == i//2
