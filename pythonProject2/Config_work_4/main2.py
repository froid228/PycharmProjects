def assembler(code):
    bc = []
    for op, *args in code:
        if op == 'move':
            b, c = args
            bc += serializer(233, [(b, 8), (c, 15)], 6)  # команда move
        elif op == 'read':
            b, c = args
            bc += serializer(128, [(b, 8), (c, 23)], 6)  # команда read
        elif op == 'write':
            b, c = args
            bc += serializer(112, [(b, 8), (c, 15)], 6)  # команда write
        elif op == 'sgn':
            b, c = args
            bc += serializer(206, [(b, 8), (c, 15)], 6)  # команда sgn
    return bc

def serializer(cmd, fields, size):
    bits = cmd
    for value, offset in fields:
        bits |= (value << offset)
    return bits.to_bytes(size, 'little')

# Тесты для ассемблера
def test_move():
    code = [("move", 76, 44)]
    bytes_result = assembler(code)
    assert bytes_result == [0xE9, 0xCB, 0x51, 0x25, 0x00, 0x00], f"Test failed: {bytes_result}"

def test_read():
    code = [("read", 110, 34)]
    bytes_result = assembler(code)
    assert bytes_result == [0x80, 0x05, 0x81, 0x23, 0x00, 0x00], f"Test failed: {bytes_result}"

def test_write():
    code = [("write", 51, 106)]
    bytes_result = assembler(code)
    assert bytes_result == [0x70, 0xE1, 0x91, 0x02, 0x00, 0x00], f"Test failed: {bytes_result}"

def test_sgn():
    code = [("sgn", 844, 555)]  # Тестируем операцию sgn
    bytes_result = assembler(code)
    assert bytes_result == [0xCE, 0x4C, 0xB3, 0x22, 0x00, 0x00], f"Test failed: {bytes_result}"

def run_tests():
    test_move()
    test_read()
    test_write()
    test_sgn()

# Интерпретатор
def interpreter(cmds):
    memory = [0] * 100  # 100 ячеек памяти
    regs = [0] * 10     # 10 регистров

    for op, *args in cmds:
        if op == "move":
            address, const = args
            regs[address] = const
        elif op == "write":
            target, source = args
            memory[regs[target]] = regs[source]
        elif op == "read":
            b, c = args
            regs[c] = memory[b]
        elif op == "sgn":
            b, c = args
            # Выполнение операции sgn
            value = memory[regs[b]]
            if value > 0:
                memory[regs[c]] = 1
            elif value < 0:
                memory[regs[c]] = -1
            else:
                memory[regs[c]] = 0

    print("Registers:", regs)
    print("Memory:", memory)

# Тестовая программа для операции sgn() над вектором
def test_program():
    # Вектор данных длины 5: [10, -20, 0, 15, -5]
    # Записываем вектор в память по адресам 0–4
    cmds = [
        ("move", 0, 10),    # Пишем 10 в регистр 0
        ("write", 0, 0),    # Записываем значение регистра 0 в память по адресу 0
        ("move", 0, -20),   # Пишем -20 в регистр 0
        ("write", 0, 1),    # Записываем значение регистра 0 в память по адресу 1
        ("move", 0, 0),     # Пишем 0 в регистр 0
        ("write", 0, 2),    # Записываем значение регистра 0 в память по адресу 2
        ("move", 0, 15),    # Пишем 15 в регистр 0
        ("write", 0, 3),    # Записываем значение регистра 0 в память по адресу 3
        ("move", 0, -5),    # Пишем -5 в регистр 0
        ("write", 0, 4),    # Записываем значение регистра 0 в память по адресу 4
    ]

    # Выполнение операции sgn() для каждого элемента вектора
    for i in range(5):
        cmds.append(("move", 0, i))      # Регистр 0 указывает на адрес i
        cmds.append(("move", 1, i + 5)) # Регистр 1 указывает на адрес результата i+5
        cmds.append(("sgn", 0, 1))      # Выполняем операцию sgn
    
    interpreter(cmds)

# Запуск тестовой программы
test_program()
