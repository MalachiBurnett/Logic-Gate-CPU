opcode_map = {
    "NOP": "0000",
    "ADD": "0001",
    "SUB": "0010",
    "XOR": "0011",
    "AND": "0100",
    "OR": "0101",
    "NAD": "0110",
    "NOR": "0111",
    "BSL": "1000",
    "BSR": "1001",
    "XNR": "1010",
    "SET": "1011",
    "MOV": "1100",
    "JMP": "1101",
    "BRH": "1110",
    "HLT": "1111",
    "EQL": "10000",
    "GTT": "10001",
    "LST": "10010",
    "CMP": "10011"
}

def parse_register(reg):
    return f"{int(reg[1:]):04b}"

def assemble_line(line):
    parts = line.split()
    
    # Ignore comments
    if line.strip().startswith(";"):
        return None
    
    if line.strip().startswith("#"):
        return "0000000000000000"

    instr = parts[0]
    opcode = opcode_map[instr]

    if instr == "NOP":
        return opcode + "0000000000000000"

    elif instr in {"ADD", "SUB", "XOR", "AND", "OR", "NAD", "NOR", "BSL", "BSR", "XNR"}:
        reg1 = parse_register(parts[1])
        reg2 = parse_register(parts[2])
        reg3 = parse_register(parts[3])
        return opcode + reg1 + reg2 + reg3

    elif instr == "SET":
        value = f"{int(parts[1]):04b}"
        reg = parse_register(parts[2])
        return opcode + value + reg + "0000"

    elif instr == "MOV":
        reg1 = parse_register(parts[1])
        reg2 = parse_register(parts[2])
        return opcode + reg1 + reg2 + "0000"

    elif instr == "JMP":
        address = f"{int(parts[1]):08b}"
        dir_bit = "1" if parts[2] == "1" else "0"
        return opcode + address + dir_bit + "000"

    elif instr == "BRH":
        address = f"{int(parts[1]):08b}"  # Convert the address to an 8-bit binary
        flag = f"{int(parts[2]):02b}"     # Convert the flag to a 2-bit binary
        dir_bit = parts[3]                # Use the direction bit directly
        return opcode + address + flag + dir_bit + "0"

    elif instr == "HLT":
        return opcode + "000000000000"

    elif instr == "EQL":
        reg1 = parse_register(parts[1])
        reg2 = parse_register(parts[2])
        return "0100" + reg1 + reg2 + "0000"

    elif instr in {"GTT", "LST", "CMP"}:
        reg1 = parse_register(parts[1])
        reg2 = parse_register(parts[2])
        return "0010" + reg1 + reg2 + "0000"

    else:
        raise ValueError(f"Unknown instruction: {instr}")

def assemble_program(lines):
    binary_lines = [assemble_line(line) for line in lines if line.strip() and not line.strip().startswith(";")]
    # Filter out None values from comments
    return [line for line in binary_lines if line is not None]