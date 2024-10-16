from .interface import call_add

import random

def test_one_byte_add():
    for i in range(256):
        for j in range(256):
            assert call_add(i,j) == i+j

def test_middle_carry():
    a = 128+255*256+100*256**2
    b = 128+0*256+100*256**2
    assert call_add(a,b) == a+b

def test_a_equals_b():
    a = 7124
    assert call_add(a,a,ma=0x1000,mb=0x1000,mc=0x1100) == a+a

def test_self_add():
    for i in range(128):
        a = random.getrandbits(128*8)
    assert call_add(a,a,ma=0x1000,mb=0x1000,mc=0x1000) == a+a

def test_large_add():
    random.seed(0x1337)
    for i in range(128):
        a = random.getrandbits(24)
        b = random.getrandbits(24)
        assert call_add(a,b) == a+b

def test_larger_add():
    random.seed(0x1337)
    for i in range(128):
        a = random.getrandbits(128*8)
        b = random.getrandbits(128*8)
        assert call_add(a,b) == a+b
