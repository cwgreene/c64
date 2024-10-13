from py65emu.cpu import CPU
from py65emu.mmu import MMU

def test_add(a,b):
    # load program
    f = open("bignum.prg", "rb").read()
    mmu = MMU([
        (0x0,0x2000, False)
    ])
    for i,b in enumerate(f[2:]):
        mmu.write(0x801+i, b)
    c = CPU(mmu, 0x818)

    mmu.write(0x1000, 3)
    mmu.write(0x1100, 3)
    for i,(a,b) in enumerate(zip([240, 25, 72],[25,82,94])):
        mmu.write(0x1000+i+1,a)
        mmu.write(0x1100+i+1,b)

    # simulate
    while c.r.pc != 0x84f:
        op = mmu.read(c.r.pc)
        print(hex(c.r.pc), hex(op), c.ops[op].args[1].__name__, c.r.a, bin(c.r.p))
        c.step()
    acc = 0
    for i in range(3):
        print(mmu.read(0x1200+i+1))
        acc += mmu.read(0x1200+i+1)*256**i
    print(acc)
    print("exited")
test_add(3,4)
