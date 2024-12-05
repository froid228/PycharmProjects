import struct
import csv
import argparse

# Ассемблер
def assembler(input_file, output_bin, log_file):
    instructions = []
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split()
                op = parts[0]
                args = list(map(int, parts[1:]))
                instructions.append((op, *args))

    binary_code = []
    log_data = []

    for op, *args in instructions:
        if op == 'load_const':  # Загрузка константы
            address, constant = args
            binary_code += serializer(233, [(address, 8), (constant, 8)], 6)
            log_data.append({"command": f"{op} {address} {constant}",
                             "binary": ' '.join(f"{x:02X}" for x in binary_code[-6:])})

        elif op == 'read_mem':  # Чтение из памяти
            dest, src = args
            binary_code += serializer(128, [(dest, 8), (src, 8)], 6)
            log_data.append({"command": f"{op} {dest} {src}",
                             "binary": ' '.join(f"{x:02X}" for x in binary_code[-6:])})

        elif op == 'write_mem':  # Запись в память
            src, dest = args
            binary_code += serializer(112, [(src, 8), (dest, 8)], 6)
            log_data.append({"command": f"{op} {src} {dest}",
                             "binary": ' '.join(f"{x:02X}" for x in binary_code[-6:])})

        elif op == 'sgn':  # Вычисление знака
            src, dest = args
            binary_code += serializer(206, [(src, 8), (dest, 8)], 6)
            log_data.append({"command": f"{op} {src} {dest}",
                             "binary": ' '.join(f"{x:02X}" for x in binary_code[-6:])})

    with open(output_bin, 'wb') as bin_file:
        bin_file.write(bytearray(binary_code))

    with open(log_file, 'w', newline='') as log_file:
        writer = csv.DictWriter(log_file, fieldnames=["command", "binary"])
        writer.writeheader()
        writer.writerows(log_data)

    print(f"Assembly complete: Binary saved to {output_bin}, log saved to {log_file}")


# Интерпретатор
def interpreter(binary_file, memory_range_start, memory_range_end, result_file):
    memory = [0] * 100

    with open(binary_file, 'rb') as bin_file:
        binary_code = bin_file.read()

    pc = 0  # Программа хранится по смещению
    while pc < len(binary_code):
        cmd = binary_code[pc:pc+6]
        op = cmd[0]

        if op == 233:  # load_const
            address = cmd[1]
            constant = cmd[3]
            memory[address] = constant
            print(f"load_const: M[{address}] = {constant}")

        elif op == 128:  # read_mem
            dest = cmd[1]
            src = cmd[3]
            memory[dest] = memory[src]
            print(f"read_mem: M[{dest}] = M[{src}]")

        elif op == 112:  # write_mem
            B = cmd[1]  # Адрес в памяти для поля B
            C = cmd[3]  # Адрес в памяти для поля C
    
            # Получаем значение из памяти по адресу B (это адрес, по которому нужно найти данные)
            B_value = memory[B]
    
            # Получаем адрес из памяти по адресу C
            C_value = memory[C]
    
            # Записываем значение в память по адресу, который хранится по адресу C
            memory[C_value] = memory[B_value]
            print(f"write_mem: M[M[{C}]] = M[{B}] -> M[{C_value}] = {memory[C_value]}")

        elif op == 206:  # sgn
            B = cmd[1]  # Адрес в памяти для поля B
            C = cmd[3]  # Адрес в памяти для поля C
    
            # Получаем значение из памяти по адресу B
            B_value = memory[B]
    
            # Теперь B_value является адресом, из которого нужно получить значение для вычисления знака
            operand_value = memory[B_value]  # Здесь происходит двойное обращение: memory[memory[B]]

            # Вычисляем знак
            if operand_value > 0:
                memory[C] = 1
            elif operand_value < 0:
                memory[C] = -1
            else:
                memory[C] = 0

            print(f"sgn: M[{C}] = sign(M[M[{B}]]) = {memory[C]}")

        pc += 6  # Переход к следующей инструкции

    with open(result_file, 'w', newline='') as result_file:
        writer = csv.writer(result_file)
        writer.writerow(['Memory Address', 'Value'])
        for i in range(memory_range_start, memory_range_end + 1):
            writer.writerow([i, memory[i]])

    print(f"Execution complete: Results saved to {result_file}")


# Сериализатор
def serializer(cmd, fields, size):
    bits = cmd
    for value, offset in fields:
        bits |= (value << offset)
    return list(bits.to_bytes(size, 'little'))


# Основная программа
def main():
    parser = argparse.ArgumentParser(description='Assembler and Interpreter')
    parser.add_argument('input_file', help='Assembly file')
    parser.add_argument('output_bin', help='Output binary file')
    parser.add_argument('log_file', help='Log file (CSV)')
    parser.add_argument('memory_range_start', type=int, help='Memory range start')
    parser.add_argument('memory_range_end', type=int, help='Memory range end')
    parser.add_argument('result_file', help='Result file (CSV)')

    args = parser.parse_args()

    assembler(args.input_file, args.output_bin, args.log_file)
    interpreter(args.output_bin, args.memory_range_start, args.memory_range_end, args.result_file)


if __name__ == "__main__":
    main()
