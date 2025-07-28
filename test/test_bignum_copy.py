from .interface import call_bignum_copy

def test_copy_one_byte():
    a = 5
    cpu, mmu, _ = call_bignum_copy(a, ma=0x1000, mb=0x1100)
    assert mmu.read(0x1000) == 1
    assert mmu.read(0x1001) == 5
    assert mmu.read(0x1100) == 1
    assert mmu.read(0x1101) == 5

def test_copy_two_bytes():
    a = 0x5625
    cpu, mmu, _ = call_bignum_copy(a, ma=0x1000, mb=0x1100)
    assert mmu.read(0x1000) == 2
    assert mmu.read(0x1001) == 0x25
    assert mmu.read(0x1002) == 0x56
    assert mmu.read(0x1100) == 2
    assert mmu.read(0x1101) == 0x25
    assert mmu.read(0x1102) == 0x56