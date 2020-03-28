import sys
from cpu import *

if len(sys.argv) != 2:
    print('Usage: ls8.py filename')
    sys.exit(1)

program = sys.argv[1]

cpu = CPU()

cpu.load(program)
cpu.run()