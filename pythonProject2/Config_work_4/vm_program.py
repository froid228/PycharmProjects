import struct
import csv
import argparse

# Ассемблер
def assembler(input_file, output_bin, log_file):
    instructions = []
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:  # Пропускаем пустые строки
                parts = line.split()
                op = parts[0]
                args = list(map(int, parts[1:]))
                instructions.append((op, *args))

    binary_code = []
    log_data = []

    for idx, (op, *args) in enumerate(instructions):
        if op == 'load_const':  # Загрузка константы
            address, constant = args
            if not (0 <= address < 100):  # Проверка на допустимость адреса памяти
                print(f"Error: Invalid memory address {address} for load_const operation")
                continue
            binary_code += serializer(233, [(address, 8), (constant, 8)], 6)
            log_data.append({"command": f"load_const {address} {constant}",
                             "binary": ' '.join(f"{x:02X}" for x in binary_code[-6:])})

        elif op == 'read_mem':  # Чтение из памяти
            dest, src = args
            if not (0 <= src < 100 and 0 <= dest < 100):
                print(f"Error: Invalid memory address {src} or {dest} for read_mem operation")
                continue
            binary_code += serializer(128, [(dest, 8), (src, 8)], 6)
            log_data.append({"command": f"read_mem {dest} {src}",
                             "binary": ' '.join(f"{x:02X}" for x in binary_code[-6:])})

        elif op == 'write_mem':  # Запись в память
            src, dest = args
            if not (0 <= src < 100 and 0 <= dest < 100):
                print(f"Error: Invalid memory address {src} or {dest} for write_mem operation")
                continue
            binary_code += serializer(112, [(src, 8), (dest, 8)], 6)
            log_data.append({"command": f"write_mem {src} {dest}",
                             "binary": ' '.join(f"{x:02X}" for x in binary_code[-6:])})

        elif op == 'move':  # Перемещение
            src, dest = args
            if not (0 <= src < 100 and 0 <= dest < 100):
                print(f"Error: Invalid memory address {src} or {dest} for move operation")
                continue
            binary_code += serializer(233, [(src, 8), (dest, 8)], 6)
            log_data.append({"command": f"move {src} {dest}",
                             "binary": ' '.join(f"{x:02X}" for x in binary_code[-6:])})

        elif op == 'sgn':  # Унарная операция
            src, dest = args
            if not (0 <= src < 100 and 0 <= dest < 100):
                print(f"Error: Invalid memory address {src} or {dest} for sgn operation")
                continue
            binary_code += serializer(206, [(src, 8), (dest, 8)], 6)
            log_data.append({"command": f"sgn {src} {dest}",
                             "binary": ' '.join(f"{x:02X}" for x in binary_code[-6:])})

        else:
            print(f"Error: Unknown operation {op}")

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

    with open(binary_file, 'rb') as bin_file:
        binary_code = bin_file.read()

    pc = 0  # Program counter

    while pc < len(binary_code):
        cmd = binary_code[pc:pc+6]
        op = cmd[0]

        try:
            if op == 233:  # Загрузка константы
                address = cmd[1] | (cmd[2] << 8)
                constant = cmd[3] | (cmd[4] << 8)
                if 0 <= address < 100:
                    memory[address] = constant
                    print(f"load_const: M{address} = {constant}")
                else:
                    print(f"Error: Invalid memory address {address} for load_const operation")

            elif op == 128:  # Чтение из памяти
                dest = cmd[1] | (cmd[2] << 8)
                src = cmd[3] | (cmd[4] << 8)
                if 0 <= src < 100 and 0 <= dest < 100:
                    memory[dest] = memory[src]
                    print(f"read_mem: M{dest} = M{src}")
                else:
                    print(f"Error: Invalid memory address {src} or {dest} for read_mem operation")

            elif op == 112:  # Запись в память
                src = cmd[1] | (cmd[2] << 8)
                dest = cmd[3] | (cmd[4] << 8)
                if 0 <= src < 100 and 0 <= dest < 100:
                    memory[dest] = memory[src]
                    print(f"write_mem: M{dest} = M{src}")
                else:
                    print(f"Error: Invalid memory address {src} or {dest} for write_mem operation")

            elif op == 233:  # move
                src = cmd[1] | (cmd[2] << 8)
                dest = cmd[3] | (cmd[4] << 8)
                if 0 <= src < 100 and 0 <= dest < 100:
                    memory[dest] = memory[src]
                    print(f"move: M{dest} = M{src}")
                else:
                    print(f"Error: Invalid memory address {src} or {dest} for move operation")

            elif op == 206:  # sgn
                src = cmd[1] | (cmd[2] << 8)
                dest = cmd[3] | (cmd[4] << 8)
                if 0 <= src < 100 and 0 <= dest < 100:
                    for i in range(5):
                        value = memory[src + i]
                        if value > 0:
                            memory[dest + i] = 1
                        elif value < 0:
                            memory[dest + i] = -1
                        else:
                            memory[dest + i] = 0
                    print(f"sgn: M{dest} = sign(M{src})")
                else:
                    print(f"Error: Invalid memory address {src} or {dest} for sgn operation")

            else:
                print(f"Error: Unknown operation code {op}")

        except IndexError as e:
            print(f"IndexError: {e}")
            break

        pc += 6  # Переход к следующей команде (6 байт на команду)

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
