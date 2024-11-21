import xml.etree.ElementTree as ET

# Функция для преобразования значения в нужный тип
def translate_value(value, value_type):
    if value_type == "string":
        return value  # Просто возвращаем строку
    elif value_type == "number":
        try:
            # Преобразуем строку в число (целое или с плавающей точкой)
            return int(value) if value.isdigit() else float(value)
        except ValueError:
            raise ValueError(f"Не удалось преобразовать значение в число: {value}")
    elif value_type == "dictionary":
        try:
            # Преобразуем строку в словарь
            return eval(value)
        except Exception:
            raise ValueError(f"Не удалось интерпретировать значение как словарь: {value}")
    else:
        raise ValueError(f"Неизвестный тип значения: {value_type}")

# Функция для обработки каждого элемента конфигурации
def parse_entry(entry):
    name = entry.find("name").text  # Извлекаем имя
    value_element = entry.find("value")  # Извлекаем значение
    
    if value_element is None:
        raise ValueError(f"Элемент <value> отсутствует в записи {name}")
    
    value_type = value_element.get("type")
    if value_type is None:
        raise ValueError(f"Отсутствует атрибут 'type' у элемента <value> для {name}")
    
    value = value_element.text  # Значение как строка
    return name, translate_value(value, value_type)  # Переводим значение в нужный тип

# Функция для парсинга XML-файла
def parse_xml(filename):
    try:
        tree = ET.parse(filename)  # Загружаем XML
        root = tree.getroot()  # Получаем корень XML
    except ET.ParseError as e:
        raise ValueError(f"Ошибка парсинга XML: {e}")

    config = []
    
    # Обрабатываем каждый элемент в корне
    for entry in root.findall("entry"):
        try:
            name, value = parse_entry(entry)  # Обрабатываем запись
            config.append(f"{name} => {value}")
        except ValueError as e:
            print(f"Ошибка при обработке записи: {e}")
    
    return config

# Функция для трансляции данных из XML в формат конфигурации
def translate_to_config(data):
    if not data:
        raise ValueError("Конфигурация пустая.")
    
    return "[\n" + ",\n".join(data) + "\n]"

# Основная функция для тестирования
def run_tests():
    # Тест 1: Конфигурация веб-сервера
    xml_data_1 = """
    <dictionary>
        <entry>
            <name>host</name>
            <value type="string">localhost</value>
        </entry>
        <entry>
            <name>port</name>
            <value type="number">8080</value>
        </entry>
        <entry>
            <name>routes</name>
            <value type="dictionary">{'home': '/', 'about': '/about'}</value>
        </entry>
    </dictionary>
    """
    print("=== Тест 1: Веб-сервер ===")
    with open("test1.xml", "w") as f:
        f.write(xml_data_1)

    try:
        data = parse_xml("test1.xml")
        config = translate_to_config(data)
        print("Результат:\n", config)
    except Exception as e:
        print("Ошибка:\n", e)

    # Тест 2: Конфигурация умного дома
    xml_data_2 = """
    <dictionary>
        <entry>
            <name>temperature</name>
            <value type="number">22</value>
        </entry>
        <entry>
            <name>lighting</name>
            <value type="dictionary">{'living_room': 'on', 'bedroom': 'off'}</value>
        </entry>
        <entry>
            <name>security</name>
            <value type="dictionary">{'alarm': 'armed', 'cameras': 'active'}</value>
        </entry>
    </dictionary>
    """
    print("\n=== Тест 2: Умный дом ===")
    with open("test2.xml", "w") as f:
        f.write(xml_data_2)

    try:
        data = parse_xml("test2.xml")
        config = translate_to_config(data)
        print("Результат:\n", config)
    except Exception as e:
        print("Ошибка:\n", e)

    # Тест 3: Некорректный XML
    invalid_xml_data = """
    <dictionary>
        <entry>
            <name>invalid</name>
            <value>missing type attribute</value>
        </entry>
    </dictionary>
    """
    print("\n=== Тест 3: Некорректный XML ===")
    with open("test_invalid.xml", "w") as f:
        f.write(invalid_xml_data)

    try:
        data = parse_xml("test_invalid.xml")
        config = translate_to_config(data)
        print("Результат:\n", config)
    except Exception as e:
        print("Ошибка:\n", e)


if __name__ == "__main__":
    run_tests()
