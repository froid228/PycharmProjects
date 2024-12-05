def assembler(code):
    bc = []
    for op, *args in code:
        if op == 'move':
            src, dest = args
            bc += serializer(233, [(src, 15), (dest, 15)], 6)  # команда move
        elif op == 'read':
            src, dest = args
            bc += serializer(128, [(src, 15), (dest, 15)], 6)  # команда read
        elif op == 'write':
            src, dest = args
            bc += serializer(112, [(src, 15), (dest, 15)], 6)  # команда write
        elif op == 'sgn':
            src, dest = args
            bc += serializer(206, [(src, 15), (dest, 15)], 6)  # команда sgn
    return bc


def serializer(cmd, fields, size):
    bits = cmd
    for value, offset in fields:
        bits |= (value << offset)
    return list(bits.to_bytes(size, 'little'))


# Интерпретатор
def interpreter(cmds):
    memory = [0] * 100  # 100 ячеек памяти

    for op, *args in cmds:
        if op == "load":
            address, value = args
            memory[address] = value
            print(f"load: M[{address}] = {value}")
        elif op == "move":
            src, dest = args
            memory[dest] = memory[src]
            print(f"move: M[{dest}] = M[{src}] ({memory[dest]})")
        elif op == "write":
            src, dest = args
            memory[dest] = src
            print(f"write: M[{dest}] = {src}")
        elif op == "sgn":
            src, dest = args
            value = memory[src]
            if value > 0:
                memory[dest] = 1
            elif value < 0:
                memory[dest] = -1
            else:
                memory[dest] = 0
            print(f"sgn: M[{dest}] = sign(M[{src}]) ({memory[dest]})")
        else:
            print(f"Unknown operation: {op}")

    print("Final Memory state:", memory)


# Тесты
def test_program():
    print("\n=== Test 1: Simple load and write ===")
    cmds = [
        ("load", 0, 100),  # Загружаем значение 100 в M[0]
        ("load", 1, -50),  # Загружаем значение -50 в M[1]
        ("write", 200, 2), # Пишем 200 в M[2]
    ]
    interpreter(cmds)

    print("\n=== Test 2: Move operation ===")
    cmds = [
        ("load", 3, 123),  # Загружаем значение 123 в M[3]
        ("move", 3, 4),    # Перемещаем значение из M[3] в M[4]
    ]
    interpreter(cmds)

    print("\n=== Test 3: sgn operation ===")
    cmds = [
        ("load", 5, 42),   # Загружаем значение 42 в M[5]
        ("load", 6, -17),  # Загружаем значение -17 в M[6]
        ("load", 7, 0),    # Загружаем значение 0 в M[7]
        ("sgn", 5, 8),     # Считаем знак M[5] и сохраняем в M[8]
        ("sgn", 6, 9),     # Считаем знак M[6] и сохраняем в M[9]
        ("sgn", 7, 10),    # Считаем знак M[7] и сохраняем в M[10]
    ]
    interpreter(cmds)

    print("\n=== Test 4: Complex operations ===")
    cmds = [
        ("load", 0, 10),   # Загружаем значение 10 в M[0]
        ("load", 1, -20),  # Загружаем значение -20 в M[1]
        ("sgn", 1, 2),     # Считаем знак M[1] и сохраняем в M[2]
        ("write", 15, 3),  # Пишем значение 15 в M[3]
        ("move", 3, 4),    # Перемещаем значение из M[3] в M[4]
        ("sgn", 0, 5),     # Считаем знак M[0] и сохраняем в M[5]
    ]
    interpreter(cmds)


# Запуск тестов
test_program()
