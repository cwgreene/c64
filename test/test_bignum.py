from py65emu.cpu import CPU
from py65emu.mmu import MMU

def mknum(a):
    arr = []
    while a:
        arr.append(a%256)
        a //= 256
    return arr

def create_add():
    # load program
    f = open("bignum.prg", "rb").read()
    mmu = MMU([
        (0x0,0x2000, False)
    ])
    for i,by in enumerate(f[2:]):
        mmu.write(0x801+i, by)
    c = CPU(mmu, 0x818)

    def call_add(a,b):
        # set address
        c.r.pc = 0x818

        a = mknum(a)
        b = mknum(b)

        # pad them to same length for zip
        a += [0]*max(len(b)-len(a),0)
        b += [0]*max(len(a)-len(b),0)

        # Write a and b
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

        # read out
        acc = 0
        length = mmu.read(0x1200)

        for i in range(length):
            #print("digit", mmu.read(0x1200+i+1))
            acc += mmu.read(0x1200+i+1)*256**i
        return acc
    return call_add

def test_add():
    call_add = create_add()
    for i in range(256):
        for j in range(256):
            assert call_add(i,j) == i+j
