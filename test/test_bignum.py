from py65emu.cpu import CPU
from py65emu.mmu import MMU

def mknum(a):
    arr = []
    while a:
        arr.append(a%256)
        a //= 256
    return arr

def test_add(a,b):
    # load program
    f = open("bignum.prg", "rb").read()
    mmu = MMU([
        (0x0,0x2000, False)
    ])
    for i,by in enumerate(f[2:]):
        mmu.write(0x801+i, by)
    c = CPU(mmu, 0x818)

    a = mknum(a)
    b = mknum(b)

    # pad them to same length for zip
    a += [0]*max(len(b)-len(a),0)
    b += [0]*max(len(a)-len(b),0)

    mmu.write(0x1000, len(a))
    mmu.write(0x1100, len(b))
    for i,(a_digit,b_digit) in enumerate(zip(a,b)):
        mmu.write(0x1000+i+1,a_digit)
        mmu.write(0x1100+i+1,b_digit)

    # simulate
    while c.r.pc != 0x84f:
        op = mmu.read(c.r.pc)
        #print(hex(c.r.pc), hex(op), c.ops[op].args[1].__name__, c.r.a, c.r.x, c.r.y, bin(c.r.p))
        c.step()
    acc = 0
    length = mmu.read(0x1200)
    #print("length",length)
    for i in range(length):
        #print("digit", mmu.read(0x1200+i+1))
        acc += mmu.read(0x1200+i+1)*256**i
    return acc
print(test_add(3,4), 3+4)
print(test_add(2741,141234), 2741+141234)
