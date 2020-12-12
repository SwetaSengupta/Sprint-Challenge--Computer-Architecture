  
"""
CPU functionality
"""

import sys

# translation of opcodes for the dispatch table

# Opcodes for human readability
HLT = 0b00000001  # Halt
LDI = 0b10000010  # Load Immediate
PRN = 0b01000111  # Print

# ALU opcodes
MUL = 0b10100010  # Multiply
ADD = 0b10100000  # Add

# Stack
PUSH = 0b01000101  # Push
POP = 0b01000110  # Pop

# Day 4 Assignment
CALL = 0b01010000  # Call
RET = 0b00010001  # Return

# new for sprint challenge
CMP = 0b10100111  # Compare
JMP = 0b01010100  # Jump to register
JEQ = 0b01010101  # Jump if E flag set
JNE = 0b01010110  # Jump if an not E flag / E is clear


class CPU:
    """Main CPU class."""

    def __init__(self):
        """
        Construct a new CPU.
        Add list properties to the `CPU` class to hold 256 bytes of memory and 8
        general-purpose registers.
        """
        self.memory = [0] * 256  # we need 256 bytes of memory - call it ram
        self.registers = [0] * 8  # we need 8 registers
        self.pc = 0  # program counter - start at 0 - can increment or change later
        self.running = True  # set program to running, this can be changed later

        self.stack_pointer = 7

        """
        The flags register `FL` holds the current flags status. These flags
        can change based on the operands given to the `CMP` opcode.
        The register is made up of 8 bits. If a particular bit is set, that flag is "true".
        `FL` bits: `00000LGE`
        * `L` Less-than: during a `CMP`, set to 1 if registerA is less than registerB,
        zero otherwise.
        * `G` Greater-than: during a `CMP`, set to 1 if registerA is greater than
        registerB, zero otherwise.
        * `E` Equal: during a `CMP`, set to 1 if registerA is equal to registerB, zero
        otherwise.
        """
        self.flag = [0] * 8


        # Dispatch table for fast lookups
        self.dispatch = {}
        self.dispatch[HLT] = self.dis_HLT
        self.dispatch[LDI] = self.dis_LDI
        self.dispatch[PRN] = self.dis_PRN

        self.dispatch[PUSH] =self.dis_PUSH
        self.dispatch[POP] = self.dis_POP

        self.dispatch[CALL] = self.dis_CALL
        self.dispatch[RET] = self.dis_RET

        self.dispatch[MUL] = self.dis_MUL
        self.dispatch[ADD] = self.dis_ADD

        self.dispatch[CMP] = self.dis_CMP
        self.dispatch[JMP] = self.dis_JMP
        self.dispatch[JEQ] = self.dis_JEQ
        self.dispatch[JNE] = self.dis_JNE

    def ram_read(self, MAR):
        """
        Memory Address Register
        The MAR contains the address that is being read or written to.
        """
        return self.memory[MAR]

    def ram_write(self, MDR, MAR):
        """
        Memory Data Register
        The MDR contains the data that was read or the data to write.
        Takes the Memory Address Register MAR and overwrites it with the Memory Data Register MDR
        """
        self.memory[MAR] = MDR


    def load(self):
        """
        Load a program into memory.
        In `load()`, you will now want to use those command line arguments to open a
        file, read in its contents line by line, and save appropriate data into RAM. 
        """
        address = 0
        filename = sys.argv[1]

        with open(filename) as f:
            for line in f:
                # handle anything commented with #
                uncomment = line.split("#")
                instruct = uncomment[0].strip()
                # handle blank lines
                if instruct == "":
                    continue
                # opcode is binary integer
                opcode = int(instruct, 2)
                self.memory[address] = opcode
                address += 1


    # day one opcode functions Halt, Print, Load Immediate
    def dis_HLT(self, IR, operand_a, operand_b):
        # if Instruction Register (IR) is halt (HLT) opcode
        # set running to false and exit while loop
        if IR == HLT:
            self.running = False

    def dis_PRN(self, IR, operand_a, operand_b=None):
        # else if the Instruction Register (IR) is Print (PRN) opcode
        # print register operand and increment Program Counter (PC)
        # elif IR == PRN:
        print(self.registers[operand_a])
        # self.pc += 2

    def dis_LDI(self, IR, operand_a, operand_b):
        # Instruction Register (IR) is Load Immediate (LDI) opcode
        # sets a specified register to a specified value
        # elif IR == LDI:
        self.registers[operand_a] = operand_b
        # self.pc += 3

    # Stack Opcode Functions Push, Pop
    def dis_PUSH(self, IR, operand_a, operand_b=None):
        # PUSH register
        # Copy the value in the given register to the address pointed to by SP
        value = self.registers[operand_a]
        # Decrement the SP
        self.registers[self.stack_pointer] -= 1
        # Push the value in the given register on the stack.
        self.memory[self.registers[self.stack_pointer]] = value

    def dis_POP(self, IR, operand_a, operand_b=None):
        # POP register
        # Pop the value at the top of the stack into the given register.
        # Copy the value from the address pointed to by `SP` to the given register.
        value = self.memory[self.registers[self.stack_pointer]]
        # Increment `SP`.
        self.registers[self.stack_pointer] += 1
        # value into the register and continue
        self.registers[operand_a] = value

    
    # Day 4 Opcode Functions Call, Return
    def dis_CALL(self, IR, operand_a, operand_b):
        """
        `CALL register`
        Calls a subroutine (function) at the address stored in the register.
        """

        self.registers[self.stack_pointer] -= 1
        # address of the ***instruction*** _directly after_ `CALL` is
        # pushed onto the stack. This allows us to return to where we left
        # off when the subroutine finishes executing.
        self.memory[self.registers[self.stack_pointer]] = self.pc + 2

        # The PC is set to the address stored in the given register.
        # We jump to that location in RAM and execute the first instruction
        # in the subroutine. The PC can move forward or backwards from
        # its current location.
        self.pc = self.registers[operand_a]

    def dis_RET(self, IR, operand_a, operand_b):
        """
        Return from subroutine.
        """
        # Pop the value from the top of the stack and store it in the `PC`.
        self.pc = self.memory[self.registers[self.stack_pointer]]

        # increment the stack pointer forward
        self.registers[self.stack_pointer] += 1

 # Sprint Challenge Opcode Functions, Compare, Jump to register,
    # Jump if E Flag set, Jump if not E flag set

    def dis_CMP(self, IR, operand_a, operand_b):
        """
        `CMP registerA registerB`
        Compare the values in two registers.
        * If they are equal, set the Equal `E` flag to 1, otherwise set it to 0.
        * If registerA is less than registerB, set the Less-than `L` flag to 1,
        otherwise set it to 0.
        * If registerA is greater than registerB, set the Greater-than `G` flag
        to 1, otherwise set it to 0.
        """
        comp_a = self.registers[operand_a]
        comp_b = self.registers[operand_b]

        """
        FL bits: 00000LGE
        L Less-than: during a CMP, set to 1 if registerA is less than registerB, zero otherwise.
        G Greater-than: during a CMP, set to 1 if registerA is greater than registerB, zero otherwise.
        E Equal: during a CMP, set to 1 if registerA is equal to registerB, zero otherwise.     
        """
        if comp_a < comp_b:
            self.flag[-3] = 1
        if comp_a > comp_b:
            self.flag[-2] = 1
        if comp_a == comp_b:
            self.flag[-1] = 1

    def dis_JMP(self, IR, operand_a, operand_b):
        """
        `JMP register`
        Jump to the address stored in the given register.
        Set the `PC` to the address stored in the given register.
        """
        self.pc = self.registers[operand_a]

    def dis_JEQ(self, IR, operand_a, operand_b):
        """
        `JEQ register`
        If `equal` flag is set (true), jump to the address stored in the given register.
        """
        # if last flag-equality is true
        if self.flag[-1] == 1:
            # then jump
            self.pc = self.registers[operand_a]
        # else increment by instruction length protocol
        else:
            IR = self.memory[self.pc]
            instruction_length = ((IR >> 6) & 0b11) + 1
            self.pc += instruction_length

    def dis_JNE(self, IR, operand_a, operand_b):
        """
        `JNE register`
        If `E` flag is clear (false, 0), jump to the address stored in the given
        register.
        """
        if self.flag[-1] == 0:
            self.pc = self.registers[operand_a]
        # else increment by instruction length protocol
        else:
            IR = self.memory[self.pc]
            instruction_length = ((IR >> 6) & 0b11) + 1
            self.pc += instruction_length

    def alu(self, op, reg_a, reg_b):
        """
        ALU operations
        Arithmetic Logic Operator
        """

        if op == "ADD":
            self.registers[reg_a] += self.registers[reg_b]
        elif op == "SUB":
            self.registers[reg_a] -= self.registers[reg_b]
        elif op == "MUL":
            self.registers[reg_a] *= self.registers[reg_b]
        elif op == "DIV":
            self.registers[reg_a] //= self.registers[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

 # ALU opcode Functions Add, Multiply
    def dis_ADD(self, IR, operand_a, operand_b):
        self.alu(op="ADD", reg_a=operand_a, reg_b=operand_b)

    def dis_MUL(self, IR, operand_a, operand_b):
        # else if the Instruction Register (IR) is Multiple (MUL) opcode
        # Multiple register operand and increment Program Counter (PC)
        # elif IR == MUL:
        #     self.registers[operand_a] = (
        #         self.registers[operand_a] * self.registers[operand_b]
        #     )

        #     self.pc += 3
        self.alu(op="MUL", reg_a=operand_a, reg_b=operand_b)


    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(
            f"TRACE: %02X | %02X %02X %02X |"
            % (
                self.pc,
                # self.fl,
                # self.ie,
                self.ram_read(self.pc),
                self.ram_read(self.pc + 1),
                self.ram_read(self.pc + 2),
            ),
            end="",
        )

        for i in range(8):
            print(" %02X" % self.registers[i], end="")

        print()


    def run(self):
        """Run the CPU.
        read the memory address that's stored in register `pc`, and store
        that result in `IR`, the _Instruction Register_. This can just be a local
        variable in `run()`.
        """

        while self.running:
            # read memory address stored in Program Counter (pc)
            # store result in Instruction Register (IR)
            IR = self.memory[self.pc]
            # separate the opcodes from operands a and operands b
            operand_a = self.ram_read(self.pc + 1)  # operand_a is the next
            operand_b = self.ram_read(self.pc + 2)  # operand_b is next after next

            instruction_length = ((IR >> 6) & 0b11) + 1

            if IR in self.dispatch:
                self.dispatch[IR](IR, operand_a, operand_b)

            strange_cases = [CALL, RET, JMP, JEQ, JNE]
            if IR not in strange_cases:
                self.pc += instruction_length

            # else - flag unknown Instruction Register (IR) @ Program Counter (PC)
            # else:
            #     print(
            #         f" *** Unknown *** \n Instruction Register # {IR} at program counter {self.pc}"
            #     )
            #     self.pc += 1