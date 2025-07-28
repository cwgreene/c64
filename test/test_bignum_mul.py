from .interface import call_mul

import random

def test_one_byte_mul():
    for i in range(1,10):
        for j in range(1,10):
            print("Multiplying", i,j)
            res = call_mul(i,j)
            print("Result of multiplication", i, j, res)
            assert res == i*j            

def test_middle_carry():
    a = 128+255*256+100*256**2
    b = 128+0*256+100*256**2
    assert call_mul(a,b) == a*b

#def test_a_equals_b():
#    a = 7124
#    assert call_mul(a,a,ma=0x1000,mb=0x1000,mc=0x1100) == a*a

# Do we want to *not* do this?
# or do we rely on self mul for squaring?
# I am tending towards making it the caller's responsibility.
#def test_self_mul():
#    for i in range(128):
#        a = random.getrandbits(128*8)
#    assert call_mul(a,a,ma=0x1000,mb=0x1000,mc=0x1000) == a*a

def test_large_mul():
    random.seed(0x1337)
    for i in range(128):
        a = random.getrandbits(24)
        b = random.getrandbits(24)
        assert call_mul(a,b) == a*b

def test_larger_add():
    random.seed(0x1337)
    for i in range(128):
        a = random.getrandbits(128*8)
        b = random.getrandbits(128*8)
        assert call_mul(a,b) == a*b
