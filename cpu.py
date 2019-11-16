"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.register = [0] * 8
        self.register[7] = 0xf4  # stack pointer
        self.pc = 0
        self.L = 0
        self.E = 0
        self.G = 0

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1
        program_name = sys.argv[1]

        with open(program_name, 'r') as f:
            for line in f:
                if line[0] is not '#' and line is not '\n':
                    instruction = line.split(' ')[0]
                    self.ram[address] = int(instruction, 2)
                    address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        # ALU is for math functions and comparisons
        # Arithmetic Logic Unit

        if op == "ADD":
            self.register[reg_a] += self.register[reg_b]
        # elif op == "SUB": etc
        elif op == 'MUL':
            self.register[reg_a] *= self.register[reg_b]
        elif op == 'CMP':
            if reg_a == reg_b:
                self.E = 1
                self.L = 0
                self.G = 0
            elif reg_a < reg_b:
                self.E = 0
                self.L = 1
                self.G = 0
            elif reg_a > reg_b:
                self.E = 0
                self.L = 0
                self.G = 1

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
            print(" %02X" % self.register[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        HLT = 0b00000001
        LDI = 0b10000010
        PRN = 0b01000111
        MUL = 0b10100010
        ADD = 0b10100000
        PUSH = 0b01000101
        POP = 0b01000110
        CMP = 0b10100111
        JMP = 0b01010100
        JEQ = 0b01010101
        JNE = 0b01010110

        halted = False
        while not halted:
            instruction = self.ram[self.pc]
            op_a = self.ram[self.pc+1]
            op_b = self.ram[self.pc+2]

            if instruction is HLT:
                halted = True
                self.pc += 1

            elif instruction is LDI:
                self.register[op_a] = op_b
                self.pc += 3

            elif instruction is PRN:
                print(self.register[op_a])
                self.pc += 2

            elif instruction is MUL:
                self.alu('MUL', op_a, op_b)
                self.pc += 3

            elif instruction is ADD:
                self.alu('ADD', op_a, op_b)
                self.pc += 3

            elif instruction is JEQ:
                if self.E == 1:
                    self.pc = self.register[op_a]
                else:
                    self.pc += 2

            elif instruction is JNE:
                if self.E == 0:
                    self.pc = self.register[op_a]
                else:
                    self.pc += 2

            elif instruction is JMP:
                self.pc = self.register[op_a]

            elif instruction is CMP:
                self.alu('CMP', self.register[op_a], self.register[op_b])
                self.pc += 3

            # Stack is useful for return addresses
            # Knows how to come back to outer function to finish out remaining task
                # Storing temporary values
                # Pass arguments to subroutines AKA functions
                # 1011 0101
                #  B5
            elif instruction is PUSH:
                self.register[7] -= 1
                self.ram[self.register[7]] = self.register[op_a]
                self.pc += 2

            elif instruction is POP:
                self.register[op_a] = self.ram[self.register[7]]
                self.register[7] += 1
                self.pc += 2

            else:
                print('Unknown instruction')

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value
