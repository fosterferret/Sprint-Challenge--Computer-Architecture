"""CPU functionality."""

import sys

ADD = 0b10100000

MUL = 0b10100010
LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
JMP = 0b01010100
JNE = 0b01010110
JEQ = 0b01010101

SP = 7


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[SP] = 0xF4
        self.pc = 0
        self.fl = 0
        self.branch_table = {
            HLT: self.HLT,
            LDI: self.LDI,
            PRN: self.PRN,
            MUL: self.ALU_MUL,
            PUSH: self.PUSH,
            POP: self.POP,
            CALL: self.CALL,
            RET: self.RET,
            ADD: self.ALU_ADD
            JMP: self.JMP,
            JNE: self.JNE,
            JEQ: self.JEQ
        }

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mdr, mar):
        self.ram[mar] = mdr

    def load(self, program):
        """Load a program into memory."""
        try:
            address = 0
            with open(program) as file:
                for line in file:
                    line = line.split('#')[0]
                    line = line.strip()
                    if line == '':
                        continue
                    instruction = int(line, 2)
                    self.ram_write(instruction, address)
                    address += 1
        except FileNotFoundError:
            print('ERROR: No valid file name')
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while True:
            ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            operand_count = ir >> 6
            instruction_length = operand_count + 1

            set_pc = ir >> 4 & 0b0001
            self.branch_table[ir](operand_a, operand_b)

            if not set_pc:
                self.pc += instruction_length

    def LDI(self, reg_num, value):
        self.reg[reg_num] = value

    def PRN(self, reg_num, _):
        print(self.reg[reg_num])

    def HLT(self, *_):
        sys.exit()

    def POP(self, reg_num, _):
        value = self.ram_read(self.reg[SP])
        self.reg[reg_num] = value
        self.reg[SP] += 1

    def PUSH(self, reg_num, _):
        value = self.reg[reg_num]
        self.reg[SP] -= 1
        self.ram_write(value, self.reg[SP])

    def ALU_MUL(self, reg_a, reg_b):
        self.reg[reg_a] *= self.reg[reg_b]
    
    def ALU_ADD(self, reg_a, reg_b):
        self.reg[reg_a] += self.reg[reg_b]

    def CALL(self, reg_num, _):
        self.reg[SP] -= 1
        return_address = self.pc + 2
        self.ram_write(return_address, self.reg[SP])
        self.pc = self.reg[reg_num]

    def RET(self, *_):
        self.pc = self.ram_read(self.reg[SP])
        self.reg[SP] += 1

    def JMP(self, reg_num, _):
        self.pc = self.reg[reg_num]

    def JNE(self, reg_num, _):
        if self.fl & 1 == 0:
            self.JMP(reg_num, _)
        else:
            self.pc += 2

    def JEQ(self, reg_num, _):
        if self.fl & 1:
            self.JMP(reg_num, _)
        else:
            self.pc += 2
