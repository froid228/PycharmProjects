import argparse
import re
import sys
import xml.etree.ElementTree as ET

def parse_args():
    parser = argparse.ArgumentParser(description="Convert XML configuration to custom configuration language.")
    parser.add_argument("input_file_path", type=str, help="Path to the input XML file")
    parser.add_argument("--output_file", type=str, help="Optional output file path for the converted configuration", default=None)
    return parser.parse_args()

def read_input_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        raise Exception(f"Input file not found: {file_path}")

def validate_xml(xml_data):
    try:
        return ET.fromstring(xml_data)
    except ET.ParseError as e:
        raise Exception(f"Invalid XML format: {e}")

def convert_to_custom_language(xml_root):
    output = []
    variables = {}  # Хранилище для вычисленных значений

    def process_element(element):
        name = element.tag
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name):
            raise Exception(f"Invalid name: '{name}'")

        # Если элемент имеет текстовое значение
        if element.text and element.text.strip():
            value = element.text.strip()

            # Если текст является ссылкой на другую переменную
            if value.startswith("!(") and value.endswith(")"):
                ref_name = value[2:-1]  # Извлекаем имя переменной
                if ref_name not in variables:
                    raise Exception(f"Undefined reference: '{ref_name}' in element '{name}'")
                value = variables[ref_name]  # Подставляем значение переменной

            elif value.isdigit():
                value = int(value)  # Преобразуем числовое значение
            else:
                raise Exception(f"Invalid value: '{value}' for key '{name}'")

            # Сохраняем переменную для последующего использования
            variables[name] = value
            output.append(f"let {name} = {value};")

        # Если элемент имеет дочерние элементы
        elif len(element):
            output.append(f"let {name} = [")
            for child in element:
                child_name = child.tag
                child_value = child.text.strip() if child.text and child.text.strip() else None

                if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", child_name):
                    raise Exception(f"Invalid name: '{child_name}' in dictionary")

                # Если текст является ссылкой на другую переменную
                if child_value and child_value.startswith("!(") and child_value.endswith(")"):
                    ref_name = child_value[2:-1]
                    if ref_name not in variables:
                        raise Exception(f"Undefined reference: '{ref_name}' in element '{child_name}'")
                    child_value = variables[ref_name]

                elif child_value and child_value.isdigit():
                    child_value = int(child_value)

                elif child_value:
                    raise Exception(f"Invalid value: '{child_value}' for key '{child_name}'")

                output.append(f"    {child_name} => {child_value},")
                variables[child_name] = child_value  # Сохраняем значение переменной

            output.append("];")
        else:
            raise Exception(f"Element '{name}' must have either a numeric value or child elements.")

    for element in xml_root:
        process_element(element)

    return "\n".join(output)

def main():
    args = parse_args()

    try:
        xml_data = read_input_file(args.input_file_path)
        xml_root = validate_xml(xml_data)
        custom_config = convert_to_custom_language(xml_root)

        if args.output_file:
            with open(args.output_file, "w", encoding="utf-8") as file:
                file.write(custom_config)
            print(f"Converted configuration written to: {args.output_file}")
        else:
            print("Converted Configuration:")
            print(custom_config)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
