import jinja2
import argparse
import re

env = jinja2.Environment()

# starts at 0x20
PETSCII = (" !\"#$%&'()*+,-./"+
           "0123456789:;<=>?"+
           "@ABCDEFGHIJKLMNO"+
           "PQRSTUVWXYZ[£]↑←")

SCREENCODE = ("@ABCDEFGHIJKLMNOPQRSTUVWXYZ[£]↑←" +
               " !\"#$%&`()*+,-./0123456789:;<=>?")
           

def filter(f):
    env.filters[f.__name__] = f
    return f

@filter
def petscii(s):
    vals = []
    for c in s:
        if c not in PETSCII:
            raise Exception(f"Invalid character {c}")
        vals.append(str(hex(PETSCII.index(c)+0x20)))
    return ",".join(vals)

@filter
def screencode(s):
    vals = []
    for c in s:
        if c not in SCREENCODE:
            raise Exception(f"Invalid character {c}")
        vals.append(str(hex(SCREENCODE.index(c))))
    return ",".join(vals)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    options = parser.parse_args()
    env.filters["petscii"]
    template = env.from_string(open(options.filename).read())
    macro_subbed = template.render()

    lines = []
    for line in macro_subbed.split("\n"):
       if re.match("^ *[^ #]*:", line):
            line = line.lstrip() 
       lines.append(line)
    print("\n".join(lines))
main()
