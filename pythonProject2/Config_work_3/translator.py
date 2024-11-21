import argparse
import xml.etree.ElementTree as ET


def parse_xml(file_path):
    """
    Читает XML-файл и преобразует его в словарь.
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Проверяем, что корневой элемент является словарем
        if root.tag != "dictionary":
            raise ValueError("Корневой элемент должен быть 'dictionary'.")

        result = []
        for entry in root:
            if entry.tag != "entry":
                raise ValueError(f"Некорректный элемент: {entry.tag}. Ожидается 'entry'.")
            
            # Проверяем наличие имени и значения
            name = entry.find("name")
            value = entry.find("value")

            if name is None or value is None:
                raise ValueError("Каждый элемент 'entry' должен содержать 'name' и 'value'.")

            # Проверяем корректность имени (имя должно быть из маленьких букв)
            if not name.text.islower() or not name.text.isalpha():
                raise ValueError(f"Имя '{name.text}' некорректно. Ожидается [a-z]+.")

            # Определяем тип значения
            if value.attrib.get("type") == "number":
                try:
                    value_content = int(value.text)
                except ValueError:
                    raise ValueError(f"Значение '{value.text}' не является числом.")
            elif value.attrib.get("type") == "dictionary":
                try:
                    value_content = eval(value.text)  # Преобразуем текст словаря в Python-объект
                    if not isinstance(value_content, dict):
                        raise ValueError(f"Значение '{value.text}' не является словарем.")
                except Exception:
                    raise ValueError(f"Значение '{value.text}' не удалось интерпретировать как словарь.")
            else:
                raise ValueError(f"Неизвестный тип значения: {value.attrib.get('type')}.")

            result.append((name.text, value_content))

        return result

    except ET.ParseError as e:
        raise ValueError(f"Ошибка парсинга XML: {e}")


def translate_to_config(data):
    """
    Преобразует данные в формат учебного конфигурационного языка.
    """
    config_lines = ["["]
    for name, value in data:
        if isinstance(value, int):
            config_lines.append(f"  {name} => {value},")
        elif isinstance(value, dict):
            config_lines.append(f"  {name} => {value},")
    config_lines.append("]")
    return "\n".join(config_lines)


def main():
    """
    Основная функция программы.
    """
    parser = argparse.ArgumentParser(description="Инструмент трансляции XML в учебный конфигурационный язык.")
    parser.add_argument("input", help="Путь к входному XML-файлу.")
    args = parser.parse_args()

    try:
        # Парсим XML
        data = parse_xml(args.input)

        # Генерируем выходной конфигурационный текст
        config = translate_to_config(data)

        # Выводим результат в стандартный вывод
        print(config)

    except ValueError as e:
        # Сообщаем об ошибках
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
