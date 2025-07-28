from typing import List
from py65emu.cpu import CPU
from py65emu.mmu import MMU

import re

def mknum(a):
    if a == 0:
        return [0]
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

class IntegerPtr:
    def __init__(self, zero_addr, ptr_addr):
        self.zero_addr = zero_addr
        self.ptr_addr = ptr_addr

class Output(IntegerPtr):
    pass

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

    def read_num(mmu, addr):
        length = mmu.read(addr)

        acc = 0
        for i in range(length):
            acc = mmu.read(addr+i+1)*256**i + acc
        return acc

    def mk_call(function, **kwargs):
        pointers = {}
        num_args : List[IntegerPtr] = {}
        output = None

        for name in kwargs:
            arg = kwargs[name]
            if isinstance(arg, Output):
                output = arg
            elif isinstance(arg, IntegerPtr):
                num_args[name] = arg
            else:
                raise ValueError(f"Unknown argument type: {type(arg)}")

        def call(**kwargs):
            # Set Location
            cpu.r.pc = syms[function]
            
            # set num
            nums = []
            for num_arg in num_args:
                if num_arg not in kwargs:
                    raise ValueError(f"Missing argument: {num_arg}")
                value = mknum(kwargs[num_arg])
                print("value:",value)
                if "m"+num_arg in kwargs:
                    ptr_addr = kwargs["m"+num_arg]
                else:
                    ptr_addr = num_args[num_arg].ptr_addr

                # place zero page
                mmu.write(num_args[num_arg].zero_addr, ptr_addr%256)
                mmu.write(num_args[num_arg].zero_addr+1, ptr_addr//256)

                #mmu.write(ptr_addr, 0)
                #for i in range(128):
                #    mmu.write(ptr_addr + i, 0)
                # copy value
                mmu.write(ptr_addr, len(value))
                for i, digit in enumerate(value):
                    mmu.write(ptr_addr + i + 1, digit)
            if output:
                # set output pointer
                mmu.write(output.zero_addr, output.ptr_addr%256)
                mmu.write(output.zero_addr+1, output.ptr_addr//256)
                mmu.write(output.ptr_addr, 0)
                for i in range(128):
                    mmu.write(output.ptr_addr + i, 0)
            steps = 0
            while cpu.r.pc != syms[function + "_end"]:
                op = mmu.read(cpu.r.pc)
                # WARNING: Debug info will slow down all 1 byte tests.
                #if cpu.r.pc in isyms:
                #    print(isyms[cpu.r.pc],end=":")
                #print(hex(cpu.r.pc), hex(op), cpu.ops[op].args[1].__name__, cpu.r.a, cpu.r.x, cpu.r.y, bin(cpu.r.p), end=" ")
                #print("|", mmu.read(mmu.read(0x11)*256+cpu.r.y), mmu.read(mmu.read(0x13)*256+cpu.r.y))
                cpu.step()
                steps += 1
            print("steps", steps)
            print("zero addr!", output.zero_addr)    
            return cpu, mmu, read_num(mmu, output.ptr_addr) if output else None
        return call
    
    def call_mul(a,b, ma=0x1000, mb=0x1100, mc=0x1200):
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
        
        for i in range(128):
            mmu.write(mc + i, 0)

        # simulate
        steps = 0
        while cpu.r.pc != syms["mul_end"]:
            op = mmu.read(cpu.r.pc)
            # WARNING: Debug info will slow down all 1 byte tests.
            if cpu.r.pc in isyms:
                print(isyms[cpu.r.pc],end=":\n")
            #opsstr = " ".join([str(a.__name__ if hasattr(a,"__name__") else str(a)) for a in cpu.ops[op].args[1:]])
            print(hex(cpu.r.pc),
               hex(op),
               cpu.ops[op].args[1].__name__,
               "A:", hex(cpu.r.a),
                "X:", hex(cpu.r.x),
                "Y:", hex(cpu.r.y),
                "p:", bin(cpu.r.p), end=" ")
            print("|", mmu.read(mmu.read(0x30)+mmu.read(0x31)*256+cpu.r.y),
                       mmu.read(0x32)+mmu.read(mmu.read(0x33)*256+cpu.r.y),
                       f"{mmu.read(ma):02x}"+f"{mmu.read(ma+1):02x}"+f"{mmu.read(ma+2):02x}",
                       f"{mmu.read(mb):02x}"+f"{mmu.read(mb+1):02x}"+f"{mmu.read(mb+2):02x}",
                       f"{mmu.read(mc):02x}"+f"{mmu.read(mc+1):02x}"+f"{mmu.read(mc+2):02x}")
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

    return {
            "add":lambda x,y, **kwargs: mk_call("add",
                                      a=IntegerPtr(0x10, 0x1000),
                                      b=IntegerPtr(0x12, 0x1100),
                                      c=Output(0x14,0x1200)
                                    )(a=x,b=y, **kwargs)[2],
            "long_shift_right": lambda x: mk_call("long_shift_right",
                                                   a=IntegerPtr(0x20, 0x2000),
                                                   b=Output(0x22, 0x2200)
                                                )(a=x)[2],

            "mul": call_mul,
            "copy_bignum": lambda x, **kwargs: mk_call("copy_bignum",
                                      a=IntegerPtr(0x60, 0x1000),
                                      b=Output(0x62, 0x1100)
                                    )(a=x, **kwargs)
            }        

env = create_environment()
print(env)
call_add = env["add"]
call_long_shift_right = env["long_shift_right"]
call_mul = env["mul"]
call_bignum_copy = env["copy_bignum"]