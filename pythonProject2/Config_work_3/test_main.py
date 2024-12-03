from main import validate_xml, convert_to_custom_language

def run_tests():
    print("Starting tests...")
    tests = [
        # Тест 1: Валидные простые элементы и словари
        {
            "name": "Valid simple and dictionary",
            "input": """
            <config>
                <constant1>42</constant1>
                <dictionary1>
                    <key1>100</key1>
                    <key2>200</key2>
                </dictionary1>
            </config>
            """,
            "expected": """let constant1 = 42;
let dictionary1 = [
    key1 => 100,
    key2 => 200,
];""",
            "should_raise": False,
        },
        # Тест 2: Элементы с числовыми значениями
        {
            "name": "Elements with numeric values",
            "input": """
            <config>
                <max_limit>100</max_limit>
                <min_limit>1</min_limit>
            </config>
            """,
            "expected": """let max_limit = 100;
let min_limit = 1;
""",
            "should_raise": False,
        },
        # Тест 3: Элементы с числовыми значениями в словаре
        {
            "name": "Dictionary with numeric values",
            "input": """
            <config>
                <settings>
                    <timeout>30</timeout>
                    <retry>3</retry>
                </settings>
            </config>
            """,
            "expected": """let settings = [
    timeout => 30,
    retry => 3,
];""",
            "should_raise": False,
        },
        # Тест 4: Элемент без значения
        {
            "name": "Element without value",
            "input": """
            <config>
                <empty_element />
            </config>
            """,
            "expected": "Error",
            "should_raise": True,
        },
        # Тест 5: Некорректное числовое значение
        {
            "name": "Invalid numeric value",
            "input": """
            <config>
                <constant1>forty-two</constant1>
            </config>
            """,
            "expected": "Error",
            "should_raise": True,
        },
        # Тест 6: Неверное имя тега
        {
            "name": "Invalid tag name",
            "input": """
            <config>
                <123invalid>42</123invalid>
            </config>
            """,
            "expected": "Error",
            "should_raise": True,
        },
        # Тест 7: Простой XML с вложенными элементами и вычислением констант
        {
            "name": "Simple XML with nested elements and constant evaluation",
            "input": """
            <config>
                <settings>
                    <width>1920</width>
                    <height>!(width)</height>
                </settings>
            </config>
            """,
            "expected": """let settings = [
    width => 1920,
    height => 1920,
];""",
            "should_raise": False,
        },
        # Тест 8: Некорректный XML
        {
            "name": "Malformed XML",
            "input": """
            <config>
                <constant1>42
            </config>
            """,
            "expected": "Error",
            "should_raise": True,
        },
        # Тест 9: Пустой файл
        {
            "name": "Empty file",
            "input": "",
            "expected": "Error",
            "should_raise": True,
        },
    ]

    for test in tests:
        print(f"Running test: {test['name']}")
        try:
            root = validate_xml(test["input"])
            output = convert_to_custom_language(root)

            if test["should_raise"]:
                print(f"❌ Test {test['name']} failed. Expected an error, but got output:\n{output}")
            else:
                # Удаляем лишние пробелы для точного сравнения
                if output.strip() == test["expected"].strip():
                    print(f"✅ Test {test['name']} passed.")
                else:
                    print(f"❌ Test {test['name']} failed. Output:\n{output}\nExpected:\n{test['expected']}")
        except Exception as e:
            if test["should_raise"]:
                print(f"✅ Test {test['name']} passed with expected error: {e}")
            else:
                print(f"❌ Test {test['name']} failed. Unexpected error: {e}")

if __name__ == "__main__":
    run_tests()
