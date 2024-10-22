# reference multiplication using
# addition and shifts
def mul(a,b):
    if a > b:
        b,a = a,b
    acc = 0 # big num
    dbl = a # big num
    rem = b # big num
    while rem:
        if rem & 1 == 0:
            dbl = dbl << 1 # long shift
            rem = rem >> 1 # long shift
        else:
            acc += dbl # long add
            rem -= 1
    return acc
print(mul(3,4))
print(mul(8,4))
print(mul(7,9))
