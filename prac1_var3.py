class SimpleAssembler:
    def __init__(self):
        self.array = [5, 1, 9, 15, 3, 80, 2, 11, 21, 6, 10, 50, 60, 75, 100]  # Пример массива
        self.memory = [0] * 256
        self.registers = [0, 0, 0]  # R0, R1, R2
        self.PC = 0
        self.running = True

    def initialize_data(self):
        N = len(self.array)           # Длина массива
        baseAddr = 101           # Начальный адрес массива

        self.memory[100] = N             # Ячейка 100 хранит длину массива
        self.memory[99] = baseAddr       # Ячейка 99 хранит начальный адрес массива

        # Запись массива в memory[baseAddr..baseAddr+N-1]
        for i, val in enumerate(self.array):
            self.memory[baseAddr + i] = val
        self.memory[150] = -1            # Ячейка 150 для результата

    def decode_instruction(self, word):
        cmdtype = (word >> 28) & 0xF
        literal = (word >> 12) & 0xFFFF
        dest = (word >> 8) & 0xF
        op1 = (word >> 4) & 0xF
        op2 = word & 0xF

        opcode_map = {
            0x1: "LOAD",
            0x2: "LOAD_IND",
            0x3: "STORE",
            0x4: "STORE_IND",
            0x5: "CMP_IND",
            0x6: "INCREMENT",
            0x7: "DECREMENT",
            0x8: "JUMP",
            0x9: "JZ",
            0xE: "NOP",
            0xF: "HALT",
        }

        mnemonic = opcode_map.get(cmdtype, "UNKNOWN")

        return {
            "cmdtype": cmdtype,
            "mnemonic": mnemonic,
            "literal": literal,
            "dest": dest,
            "op1": op1,
            "op2": op2
        }

    def execute_instruction(self):
        if self.PC + 3 >= len(self.memory):
            print(f"PC={self.PC}: Выход за пределы памяти!")
            self.running = False
            return

        word = (self.memory[self.PC] << 24) | (self.memory[self.PC + 1] << 16) | (self.memory[self.PC + 2] << 8) | self.memory[self.PC + 3]

        decoded = self.decode_instruction(word)

        mnemonic = decoded["mnemonic"]
        literal = decoded["literal"]
        dest = decoded["dest"]
        op1 = decoded["op1"]
        op2 = decoded["op2"]

        print(f"Executing: PC={self.PC}, Instruction={mnemonic}, Registers={self.registers}, Mem150={self.memory[150]}")

        if mnemonic == "LOAD":
            if dest < len(self.registers):
                self.registers[dest] = self.memory[literal]
        elif mnemonic == "LOAD_IND":
            if dest < len(self.registers) and op2 < len(self.registers):
                mem_addr = self.registers[op2]
                if 0 <= mem_addr < len(self.memory):
                    self.registers[dest] = self.memory[mem_addr]
        elif mnemonic == "STORE":
            if dest < len(self.registers):
                self.memory[literal] = self.registers[dest]
        elif mnemonic == "STORE_IND":
            if dest < len(self.registers) and op2 < len(self.registers):
                mem_addr = self.registers[op2]
                if 0 <= mem_addr < len(self.memory):
                    self.memory[mem_addr] = self.registers[dest]
        elif mnemonic == "CMP_IND":
            if dest < len(self.registers) and op2 < len(self.registers):
                mem_addr = self.registers[op2]
                if 0 <= mem_addr < len(self.memory):
                    if self.memory[mem_addr] > self.registers[dest]:
                        self.registers[dest] = self.memory[mem_addr]
        elif mnemonic == "INCREMENT":
            if dest < len(self.registers):
                self.registers[dest] += 1
        elif mnemonic == "DECREMENT":
            if dest < len(self.registers):
                self.registers[dest] -= 1
        elif mnemonic == "JUMP":
            self.PC = literal * 4
            return
        elif mnemonic == "JZ":
            if op2 < len(self.registers):
                if self.registers[op2] == 0:
                    self.PC = literal * 4
                    return
        elif mnemonic == "NOP":
            pass
        elif mnemonic == "HALT":
            self.running = False
            return
        else:
            print(f"Неизвестная команда: {mnemonic}")

        self.PC += 4

    def run_program(self):
        self.PC = 0
        self.running = True
        while self.running and self.PC < len(self.memory):
            self.execute_instruction()

        print("\nExecution finished.")
        print("Array:", self.array)
        print("Final Registers:", self.registers)
        print("Memory[150]:", self.memory[150])

    def assemble_and_load_program(self, program):
        opcode_map_rev = {
            "LOAD": 0x1,
            "LOAD_IND": 0x2,
            "STORE": 0x3,
            "STORE_IND": 0x4,
            "CMP_IND": 0x5,
            "INCREMENT": 0x6,
            "DECREMENT": 0x7,
            "JUMP": 0x8,
            "JZ": 0x9,
            "NOP": 0xE,
            "HALT": 0xF,
        }

        def encode_instruction(mnemonic, addr1, addr2):
            cmdtype = opcode_map_rev.get(mnemonic, 0x0)

            literal = 0
            dest = 0
            op1 = 0
            op2 = 0

            if mnemonic == "LOAD":
                dest = addr1
                literal = addr2
            elif mnemonic == "LOAD_IND":
                dest = addr1
                op2 = addr2
            elif mnemonic == "STORE":
                dest = addr1
                literal = addr2
            elif mnemonic == "STORE_IND":
                dest = addr1
                op2 = addr2
            elif mnemonic == "CMP_IND":
                dest = addr1
                op2 = addr2
            elif mnemonic in ["INCREMENT", "DECREMENT"]:
                dest = addr1
            elif mnemonic == "JUMP":
                literal = addr1
            elif mnemonic == "JZ":
                literal = addr1
                op2 = addr2
            elif mnemonic in ["NOP", "HALT"]:
                pass

            word = (cmdtype << 28) | ((literal & 0xFFFF) << 12) | ((dest & 0xF) << 8) | ((op1 & 0xF) << 4) | (op2 & 0xF)
            return word

        machine_code = [encode_instruction(*instr) for instr in program]
        program_start = 0
        for i, word in enumerate(machine_code):
            self.memory[program_start + i * 4] = (word >> 24) & 0xFF
            self.memory[program_start + i * 4 + 1] = (word >> 16) & 0xFF
            self.memory[program_start + i * 4 + 2] = (word >> 8) & 0xFF
            self.memory[program_start + i * 4 + 3] = word & 0xFF

    def read_program_from_file(self, file_path):
        program = []
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith(';'):
                    continue
                parts = line.replace(",", "").split()
                mnemonic = parts[0]
                a1 = int(parts[1][1:]) if len(parts) > 1 and parts[1].startswith("R") else int(parts[1]) if len(parts) > 1 else 0
                a2 = int(parts[2][1:]) if len(parts) > 2 and parts[2].startswith("R") else int(parts[2]) if len(parts) > 2 else 0
                program.append((mnemonic, a1, a2))
        return program

if __name__ == "__main__":
    assembler = SimpleAssembler()
    assembler.initialize_data()

    choice = input("Enter '1' to input instructions manually or '2' to load from file: ")
    if choice == '1':
        program = []
        print("Enter instructions (e.g., LOAD R0, 100). Type 'END' to finish:")
        while True:
            line = input().strip()
            if line.upper() == "END":
                break
            parts = line.replace(",", "").split()
            mnemonic = parts[0]
            a1 = int(parts[1][1:]) if len(parts) > 1 and parts[1].startswith("R") else int(parts[1]) if len(parts) > 1 else 0
            a2 = int(parts[2][1:]) if len(parts) > 2 and parts[2].startswith("R") else int(parts[2]) if len(parts) > 2 else 0
            program.append((mnemonic, a1, a2))
    elif choice == '2':
        file_path = "program.txt"
        program = assembler.read_program_from_file(file_path)
    else:
        print("Invalid choice.")
        exit()

    assembler.assemble_and_load_program(program)
    assembler.run_program()
