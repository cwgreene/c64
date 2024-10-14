from py65emu.cpu import CPU
from py65emu.mmu import MMU

import re
import random

def mknum(a):
    arr = []
    while a:
        arr.append(a%256)
        a //= 256
    return arr

def load_syms(symfile):
    syms = open(symfile).read()
    syms_dict = {}
    for line in syms.split("\n"):
        if line.startswith("-") or len(line)==0:
            continue
        res = re.findall("^([^ ]*) *([^ ]*)", line)
        print(res)
        sym, address = res[0]
        syms_dict[sym] = int(address,16)
    return syms_dict

def invert_syms(syms):
    isyms = {}  
    for s in syms:
        addr = syms[s]
        isyms[addr] = isyms.get(addr, []) + [s]
    return isyms

def create_add():
    # load program
    f = open("bignum.prg", "rb").read()
    syms = load_syms("bignum.sym")
    isyms = invert_syms(syms)
    mmu = MMU([
        (0x0,0x2000, False)
    ])
    for i,by in enumerate(f[2:]):
        mmu.write(0x801+i, by)
    cpu = CPU(mmu, syms["add"])

    def call_add(a,b):
        # set address
        cpu.r.pc = 0x818

        a = mknum(a)
        b = mknum(b)

        # pad them to same length for zip
        a += [0]*max(len(b)-len(a),0)
        b += [0]*max(len(a)-len(b),0)
        print(a,b)
        # Write a and b
        mmu.write(0x1000, len(a))
        mmu.write(0x1100, len(b))
        for i,(a_digit,b_digit) in enumerate(zip(a,b)):
            mmu.write(0x1000+i+1,a_digit)
            mmu.write(0x1100+i+1,b_digit)

        # simulate
        while cpu.r.pc != syms["add_end"]:
            op = mmu.read(cpu.r.pc)
            # WARNING: Debug info will slow down all 1 byte tests.
            #if cpu.r.pc in isyms:
            #    print(isyms[cpu.r.pc],end=":")
            #print(hex(cpu.r.pc), hex(op), cpu.ops[op].args[1].__name__, cpu.r.a, cpu.r.x, cpu.r.y, bin(cpu.r.p), end=" ")
            #print("|", mmu.read(0x1000+cpu.r.y), mmu.read(0x1100+cpu.r.y))
            cpu.step()

        # read out
        acc = 0
        length = mmu.read(0x1200)

        c = []
        for i in range(length):
            #print("digit", mmu.read(0x1200+i+1))
            c.append(mmu.read(0x1200+i+1))
            acc += mmu.read(0x1200+i+1)*256**i
        print(c)
        return acc
    return call_add

def test_one_byte_add():
    call_add = create_add()
    for i in range(256):
        for j in range(256):
            assert call_add(i,j) == i+j

def test_middle_carry():
    call_add = create_add()
    a = 128+255*256+100*256**2
    b = 128+0*256+100*256**2
    assert call_add(a,b) == a+b

def test_large_add():
    call_add = create_add()
    random.seed(0x1337)
    for i in range(128):
        a = random.getrandbits(24)
        b = random.getrandbits(24)
        assert call_add(a,b) == a+b
