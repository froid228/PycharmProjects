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
        if op == "move":
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

    print("Memory state:", memory)


# Тестовая программа для операции sgn() над вектором
def test_program():
    # Вектор данных длины 5: [10, -20, 0, 15, -5]
    # Записываем вектор в память по адресам 0–4
    cmds = [
        ("write", 10, 0),  # Записываем 10 в память по адресу 0
        ("write", -20, 1), # Записываем -20 в память по адресу 1
        ("write", 0, 2),   # Записываем 0 в память по адресу 2
        ("write", 15, 3),  # Записываем 15 в память по адресу 3
        ("write", -5, 4),  # Записываем -5 в память по адресу 4
    ]

    # Выполнение операции sgn() для каждого элемента вектора
    for i in range(5):
        cmds.append(("sgn", i, i + 5))  # Считаем знак значения из памяти[i], результат в памяти[i+5]
    
    interpreter(cmds)


# Запуск тестовой программы
test_program()
