from py65emu.cpu import CPU
from py65emu.mmu import MMU

import re

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

def create_environment():
    # load program
    f = open("bignum.prg", "rb").read()
    syms = load_syms("bignum.sym")
    isyms = invert_syms(syms)
    mmu = MMU([
        (0x0,0x3000, False)
    ])
    for i,by in enumerate(f[2:]):
        mmu.write(0x801+i, by)
    cpu = CPU(mmu, syms["add"])

    def call_add(a,b, ma=0x1000, mb=0x1100, mc=0x1200):
        # set address
        cpu.r.pc = syms["add"]

        a = mknum(a)
        b = mknum(b)

        # pad them to same length for zip
        a += [0]*max(len(b)-len(a),0)
        b += [0]*max(len(a)-len(b),0)
        print(a,b)
        # Write *a, *b, *c
        for i, m in enumerate([ma,mb,mc]):
            mmu.write(0x10+2*i,m % 256)
            mmu.write(0x10+2*i+1,m >> 8)

        # write a, b
        mmu.write(ma, len(a))
        mmu.write(mb, len(b))
        for i,(a_digit,b_digit) in enumerate(zip(a,b)):
            mmu.write(ma+i+1,a_digit)
            mmu.write(mb+i+1,b_digit)

        # simulate
        steps = 0
        while cpu.r.pc != syms["add_end"]:
            op = mmu.read(cpu.r.pc)
            # WARNING: Debug info will slow down all 1 byte tests.
            #if cpu.r.pc in isyms:
            #    print(isyms[cpu.r.pc],end=":")
            #print(hex(cpu.r.pc), hex(op), cpu.ops[op].args[1].__name__, cpu.r.a, cpu.r.x, cpu.r.y, bin(cpu.r.p), end=" ")
            #print("|", mmu.read(mmu.read(0x11)*256+cpu.r.y), mmu.read(mmu.read(0x13)*256+cpu.r.y))
            cpu.step()
            steps += 1
        print("steps", steps)
        # read out
        acc = 0
        length = mmu.read(mc)

        c = []
        for i in range(length):
            #print("digit", mmu.read(0x1200+i+1))
            c.append(mmu.read(mc+i+1))
            acc += mmu.read(mc+i+1)*256**i
        print(c)
        return acc

    def call_lsr(a, ma=0x2000):
        # set address
        cpu.r.pc = syms["long_shift_right"]

        # Write *a
        for i, m in enumerate([ma]):
            mmu.write(0x20+2*i,m % 256)
            mmu.write(0x20+2*i+1,m >> 8)
        a = mknum(a)

        # write a
        mmu.write(ma, len(a))
        for i,a_digit in enumerate(a):
            mmu.write(ma+i+1,a_digit)

        # simulate
        steps = 1
        while cpu.r.pc != syms["long_shift_right_end"]:
            op = mmu.read(cpu.r.pc)
            # WARNING: Debug info will slow down all 1 byte tests.
            #if cpu.r.pc in isyms:
            #    print(isyms[cpu.r.pc],end=":")
            #print(hex(cpu.r.pc), hex(op), cpu.ops[op].args[1].__name__, cpu.r.a, cpu.r.x, cpu.r.y, bin(cpu.r.p), end=" ")
            #print("|", mmu.read(mmu.read(0x11)*256+cpu.r.y), mmu.read(mmu.read(0x13)*256+cpu.r.y)) 
            steps += 1
            cpu.step()
        print("steps", steps)
        # read out
        acc = 0
        length = mmu.read(ma)

        c = []
        for i in range(length):
            #print("digit", mmu.read(0x1200+i+1))
            c.append(mmu.read(ma+i+1))
            acc += mmu.read(ma+i+1)*256**i
        print(c)
        return acc
    
    def call_mul(a,b, ma=0x1000, mb=0x1100, mdbl=0x1200, mc=0x1300):
        # set address
        mul_start = 0x30
        cpu.r.pc = syms["mul"]

        a = mknum(a)
        print(a)
        b = mknum(b)
        print(b)

        # pad them to same length for zip
        a += [0]*max(len(b)-len(a),0)
        b += [0]*max(len(a)-len(b),0)
        print("a",a,"b",b)
        # Write *a, *b, *c
        for i, m in enumerate([ma,mb,mc]):
            mmu.write(mul_start+2*i,m % 256)
            mmu.write(mul_start+2*i+1,m >> 8)

        # write a, b
        mmu.write(ma, len(a))
        mmu.write(mb, len(b))
        for i,(a_digit,b_digit) in enumerate(zip(a,b)):
            mmu.write(ma+i+1,a_digit)
            mmu.write(mb+i+1,b_digit)

        # simulate
        steps = 0
        while cpu.r.pc != syms["mul_end"]:
            op = mmu.read(cpu.r.pc)
            # WARNING: Debug info will slow down all 1 byte tests.
            if cpu.r.pc in isyms:
                print(isyms[cpu.r.pc],end=":")
            print(hex(cpu.r.pc),
                hex(op),
                cpu.ops[op].args[1].__name__,
                "A:", cpu.r.a,
                "X:", cpu.r.x,
                "Y:", cpu.r.y,
                "p:", bin(cpu.r.p), end=" ")
            print("|", mmu.read(mmu.read(0x30)+mmu.read(0x31)*256+cpu.r.y),
                       mmu.read(0x32)+mmu.read(mmu.read(0x33)*256+cpu.r.y))
            cpu.step()
            steps += 1
        print("steps", steps)
        # read out
        acc = 0
        length = mmu.read(mc)

        c = []
        for i in range(length):
            #print("digit", mmu.read(0x1200+i+1))
            c.append(mmu.read(mc+i+1))
            acc += mmu.read(mc+i+1)*256**i
        print(c)
        return acc

    return {"add":call_add, "long_shift_right": call_lsr, "mul": call_mul}

env = create_environment()
print(env)
call_add = env["add"]
call_long_shift_right = env["long_shift_right"]
call_mul = env["mul"]
