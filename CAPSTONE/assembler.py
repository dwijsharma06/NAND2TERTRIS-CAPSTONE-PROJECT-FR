import sys
from pathlib import Path

# Hack assembly language tables
DEST = {
    "": "000", "M": "001", "D": "010", "MD": "011",
    "A": "100", "AM": "101", "AD": "110", "AMD": "111"
}

JUMP = {
    "": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"
}

COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "M": "1110000",
    "!D": "0001101", "!A": "0110001", "!M": "1110001",
    "-D": "0001111", "-A": "0110011", "-M": "1110011",
    "D+1": "0011111", "A+1": "0110111", "M+1": "1110111",
    "D-1": "0001110", "A-1": "0110010", "M-1": "1110010",
    "D+A": "0000010", "D+M": "1000010",
    "D-A": "0010011", "D-M": "1010011",
    "A-D": "0000111", "M-D": "1000111",
    "D&A": "0000000", "D&M": "1000000",
    "D|A": "0010101", "D|M": "1010101"
}

PREDEFINED = {
    "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
    "SCREEN": 16384, "KBD": 24576
}
for i in range(16):
    PREDEFINED[f"R{i}"] = i


class AssemblerError(Exception):
    pass


def clean_source(path):
    """Return (original_line_number, cleaned_instruction) pairs."""
    instructions = []
    with open(path, "r", encoding="utf-8") as source:
        for line_number, raw_line in enumerate(source, start=1):
            line = raw_line.split("//", 1)[0].strip()
            if line:
                instructions.append((line_number, line))
    return instructions


def first_pass(instructions):
    """Build the label table; ROM addresses count instructions only."""
    symbols = PREDEFINED.copy()
    rom_address = 0
    seen_labels = set()

    for line_number, instruction in instructions:
        if instruction.startswith("(") and instruction.endswith(")"):
            label = instruction[1:-1].strip()
            if not label:
                raise AssemblerError(f"Line {line_number}: empty label")

            if label in seen_labels:
                print(f"Warning: duplicate label '{label}' on line {line_number}")
            else:
                seen_labels.add(label)

            # Keep the first definition, so later duplicates do not overwrite it.
            if label not in symbols:
                symbols[label] = rom_address
        else:
            rom_address += 1

    return symbols


def encode_a_instruction(value, line_number):
    try:
        address = int(value)
    except ValueError:
        raise AssemblerError(f"Line {line_number}: invalid A-instruction '@{value}'")

    if not 0 <= address <= 32767:
        raise AssemblerError(
            f"Line {line_number}: A-instruction value must be between 0 and 32767"
        )

    return format(address, "016b")


def encode_c_instruction(instruction, line_number):
    if instruction.count("=") > 1 or instruction.count(";") > 1:
        raise AssemblerError(f"Line {line_number}: invalid C-instruction")

    if "=" in instruction:
        dest, remainder = instruction.split("=", 1)
    else:
        dest, remainder = "", instruction

    if ";" in remainder:
        comp, jump = remainder.split(";", 1)
    else:
        comp, jump = remainder, ""

    dest, comp, jump = dest.strip(), comp.strip(), jump.strip()

    if comp not in COMP:
        raise AssemblerError(
            f"Line {line_number}: invalid computation '{comp}'"
        )
    if dest not in DEST:
        raise AssemblerError(f"Line {line_number}: invalid destination '{dest}'")
    if jump not in JUMP:
        raise AssemblerError(f"Line {line_number}: invalid jump '{jump}'")

    return "111" + COMP[comp] + DEST[dest] + JUMP[jump]


def assemble(input_path):
    instructions = clean_source(input_path)
    symbols = first_pass(instructions)
    next_variable_address = 16
    machine_code = []

    for line_number, instruction in instructions:
        if instruction.startswith("(") and instruction.endswith(")"):
            continue

        if instruction.startswith("@"):
            symbol = instruction[1:].strip()
            if not symbol:
                raise AssemblerError(f"Line {line_number}: missing A-instruction value")

            if symbol.isdigit():
                binary = encode_a_instruction(symbol, line_number)
            else:
                if symbol not in symbols:
                    symbols[symbol] = next_variable_address
                    next_variable_address += 1
                binary = format(symbols[symbol], "016b")
        else:
            binary = encode_c_instruction(instruction, line_number)

        machine_code.append(binary)

    output_path = Path(input_path).with_suffix(".hack")
    output_path.write_text("\n".join(machine_code) + "\n", encoding="utf-8")
    print(f"Assembly successful: {output_path}")
    print(f"Generated {len(machine_code)} machine instructions.")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 assembler.py <file.asm>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.is_file():
        print(f"Error: file not found: {input_path}")
        sys.exit(1)

    try:
        assemble(input_path)
    except AssemblerError as error:
        print(f"Assembly error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
