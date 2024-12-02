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

    def process_element(element):
        name = element.tag
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name):
            raise Exception(f"Invalid name: '{name}'")

        if element.text and element.text.strip().isdigit():
            value = int(element.text.strip())
            output.append(f"let {name} = {value};")
        elif len(element):
            output.append(f"let {name} = [")
            for child in element:
                child_name, child_value = child.tag, child.text.strip()
                if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", child_name):
                    raise Exception(f"Invalid name: '{child_name}' in dictionary")
                if not child_value.isdigit():
                    raise Exception(f"Invalid value: '{child_value}' for key '{child_name}'")
                output.append(f"    {child_name} => {child_value},")
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
