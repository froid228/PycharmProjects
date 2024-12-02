import struct
import csv
import argparse

# Ассемблер
def assembler(input_file, output_bin, log_file):
    instructions = []
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:  # пропускаем пустые строки
                parts = line.split()
                op = parts[0]
                args = list(map(int, parts[1:]))
                instructions.append((op, *args))

    binary_code = []
    log_data = []

    for idx, (op, *args) in enumerate(instructions):
        if op == 'move':
            b, c = args
            if not (0 <= b < 10) or not (0 <= c < 65536):  # проверка на допустимость значений
                print(f"Error: Invalid register index {b} or memory address {c} for move operation")
                continue
            binary_code += serializer(233, [(b, 8), (c, 15)], 6)  # команда move
            log_data.append({"command": f"move {b} {c}", "binary": ' '.join(f"{x:02X}" for x in binary_code[-6:])})
        elif op == 'read':
            b, c = args
            if not (0 <= b < 10) or not (0 <= c < 100):  # проверка на допустимость значений
                print(f"Error: Invalid register index {b} or memory address {c} for read operation")
                continue
            binary_code += serializer(128, [(b, 8), (c, 23)], 6)  # команда read
            log_data.append({"command": f"read {b} {c}", "binary": ' '.join(f"{x:02X}" for x in binary_code[-6:])})
        elif op == 'write':
            b, c = args
            if not (0 <= b < 10) or not (0 <= c < 100):  # проверка на допустимость значений
                print(f"Error: Invalid register index {b} or memory address {c} for write operation")
                continue
            binary_code += serializer(112, [(b, 8), (c, 15)], 6)  # команда write
            log_data.append({"command": f"write {b} {c}", "binary": ' '.join(f"{x:02X}" for x in binary_code[-6:])})
        elif op == 'sgn':
            b, c = args
            if not (0 <= b < 10) or not (0 <= c < 100):  # проверка на допустимость значений
                print(f"Error: Invalid register index {b} or memory address {c} for sgn operation")
                continue
            binary_code += serializer(206, [(b, 8), (c, 15)], 6)  # команда sgn
            log_data.append({"command": f"sgn {b} {c}", "binary": ' '.join(f"{x:02X}" for x in binary_code[-6:])})

    with open(output_bin, 'wb') as bin_file:
        bin_file.write(bytearray(binary_code))

    with open(log_file, 'w', newline='') as log_file:
        writer = csv.DictWriter(log_file, fieldnames=["command", "binary"])
        writer.writeheader()
        writer.writerows(log_data)

    print(f"Assembly complete: Binary file saved to {output_bin} and log saved to {log_file}")


def serializer(cmd, fields, size):
    bits = cmd
    for value, offset in fields:
        bits |= (value << offset)
    return list(bits.to_bytes(size, 'little'))


# Интерпретатор
def interpreter(binary_file, memory_range_start, memory_range_end, output_result_file):
    memory = [0] * 100  # 100 ячеек памяти
    regs = [0] * 10     # 10 регистров

    with open(binary_file, 'rb') as bin_file:
        binary_code = bin_file.read()

    pc = 0  # Program counter

    while pc < len(binary_code):
        cmd = binary_code[pc:pc+6]
        op = cmd[0]

        # Перед выполнением команды проверяем индексы
        try:
            if op == 233:  # move (6 байт)
                b = cmd[1] | (cmd[2] << 8)
                c = cmd[3] | (cmd[4] << 8)
                if 0 <= b < 10 and 0 <= c < 65536:
                    regs[b] = c
                    print(f"move: R{b} = {c}")
                else:
                    print(f"Error: Invalid register index {b} or memory address {c} for move operation")
            elif op == 128:  # read (6 байт)
                b = cmd[1] | (cmd[2] << 8)
                c = cmd[3] | (cmd[4] << 8)
                if 0 <= b < 10 and 0 <= c < 100:
                    regs[b] = memory[c]
                    print(f"read: R{b} = M{c}")
                else:
                    print(f"Error: Invalid register or memory address for read operation")
            elif op == 112:  # write (6 байт)
                b = cmd[1] | (cmd[2] << 8)
                c = cmd[3] | (cmd[4] << 8)
                if 0 <= b < 10 and 0 <= c < 100:
                    memory[regs[b]] = regs[c]
                    print(f"write: M{regs[b]} = R{c}")
                else:
                    print(f"Error: Invalid register or memory address for write operation")
            elif op == 206:  # sgn (6 байт)
                b = cmd[1] | (cmd[2] << 8)
                c = cmd[3] | (cmd[4] << 8)
                if 0 <= b < 10 and 0 <= c < 100:
                    value = memory[regs[b]]
                    if value > 0:
                        memory[regs[c]] = 1
                    elif value < 0:
                        memory[regs[c]] = -1
                    else:
                        memory[regs[c]] = 0
                    print(f"sgn: M{regs[c]} = sign(M{regs[b]})")

        except IndexError as e:
            print(f"IndexError: {e}")
            break

        pc += 6  # Move to the next command (6 bytes per command)

    # Сохраняем результат в CSV
    with open(output_result_file, 'w', newline='') as result_file:
        writer = csv.writer(result_file)
        writer.writerow(['Memory Address', 'Value'])
        for i in range(memory_range_start, memory_range_end + 1):
            writer.writerow([i, memory[i]])

    print(f"Execution complete: Results saved to {output_result_file}")


# Основная программа
def main():
    parser = argparse.ArgumentParser(description='Assembler and Interpreter for УВМ')
    parser.add_argument('input_file', help='Path to the input assembly file')
    parser.add_argument('output_bin', help='Path to save the binary file')
    parser.add_argument('log_file', help='Path to save the log file (CSV)')
    parser.add_argument('memory_range_start', type=int, help='Start address for memory range')
    parser.add_argument('memory_range_end', type=int, help='End address for memory range')
    parser.add_argument('result_file', help='Path to save the execution result')

    args = parser.parse_args()

    assembler(args.input_file, args.output_bin, args.log_file)
    interpreter(args.output_bin, args.memory_range_start, args.memory_range_end, args.result_file)


if __name__ == "__main__":
    main()
