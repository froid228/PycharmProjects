from dependency_visualizer import (
    read_config,
    parse_dependencies,
    generate_dot,
    save_dot_to_file,
    render_graph,
)
import os


def test_read_config():
    print("Тест: Чтение конфигурации")
    config = read_config("config.ini")
    assert "graphviz_path" in config, "Ошибка: Путь к Graphviz отсутствует в конфигурации."
    assert "package_path" in config, "Ошибка: Путь к пакету отсутствует в конфигурации."
    assert "output_path" in config, "Ошибка: Путь к выходному файлу отсутствует в конфигурации."
    assert "repository_url" in config, "Ошибка: URL репозитория отсутствует в конфигурации."
    print("Проверка пройдена: Чтение конфигурации.\n")


def test_parse_dependencies():
    print("Тест: Разбор зависимостей")
    dependencies = parse_dependencies("/path/to/package.apk", "http://example.com/repository")
    assert "package" in dependencies, "Ошибка: Зависимости для пакета не найдены."
    assert "libA" in dependencies["package"], "Ошибка: Зависимость libA не найдена."
    assert "libB" in dependencies["package"], "Ошибка: Зависимость libB не найдена."
    print("Проверка пройдена: Разбор зависимостей.\n")


def test_generate_dot():
    print("Тест: Генерация DOT-файла")
    dependencies = {
        "package": ["libA", "libB"],
        "libA": ["libC"],
        "libB": ["libD", "libE"],
        "libD": ["libF"],
    }
    dot_content = generate_dot(dependencies)
    assert "digraph Dependencies {" in dot_content, "Ошибка: Начало DOT-файла отсутствует."
    assert '"package" -> "libA";' in dot_content, "Ошибка: Связь package -> libA отсутствует."
    assert '"libB" -> "libE";' in dot_content, "Ошибка: Связь libB -> libE отсутствует."
    print("Проверка пройдена: Генерация DOT-файла.\n")


def test_save_dot_to_file():
    print("Тест: Сохранение DOT-файла")
    dot_content = 'digraph Dependencies {\n    "package" -> "libA";\n}'
    output_path = "test_output"
    dot_path = save_dot_to_file(dot_content, output_path)
    assert os.path.exists(dot_path), "Ошибка: DOT-файл не был создан."
    with open(dot_path, "r") as f:
        content = f.read()
        assert "digraph Dependencies {" in content, "Ошибка: Содержимое DOT-файла некорректно."
    os.remove(dot_path)  # Удаляем файл после теста
    print("Проверка пройдена: Сохранение DOT-файла.\n")


def test_render_graph():
    print("Тест: Рендеринг графа с помощью Graphviz")
    dot_content = 'digraph Dependencies {\n    "package" -> "libA";\n}'
    output_path = "test_graph"
    dot_path = save_dot_to_file(dot_content, output_path)
    graphviz_path = "/usr/bin/dot"  # Убедитесь, что путь правильный
    png_path = render_graph(dot_path, graphviz_path, output_path)
    assert os.path.exists(png_path), "Ошибка: PNG-файл не был создан."
    os.remove(dot_path)  # Удаляем DOT-файл после теста
    os.remove(png_path)  # Удаляем PNG-файл после теста
    print("Проверка пройдена: Рендеринг графа.\n")


if __name__ == "__main__":
    try:
        test_read_config()
        test_parse_dependencies()
        test_generate_dot()
        test_save_dot_to_file()
        test_render_graph()
        print("Все тесты пройдены успешно!")
    except AssertionError as e:
        print(f"Тест завершился неудачей: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
