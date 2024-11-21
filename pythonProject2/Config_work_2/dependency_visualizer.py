import os
import configparser
import subprocess
from pathlib import Path
import argparse


def read_config(config_path):
    """Читает конфигурационный файл и возвращает параметры."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Конфигурационный файл {config_path} не найден.")
    
    config = configparser.ConfigParser()
    config.read(config_path)
    
    try:
        return {
            "graphviz_path": config["Paths"]["graphviz_path"],
            "package_path": config["Paths"]["package_path"],
            "output_path": config["Paths"]["output_path"],
            "repository_url": config["Paths"]["repository_url"],
        }
    except KeyError as e:
        raise ValueError(f"Отсутствует обязательный параметр в конфигурации: {e}")


def parse_dependencies(package_path, repository_url):
    """
    Эмулирует анализ APK-пакета для получения зависимостей.
    Здесь используется статическая структура для демонстрации.
    """
    if not os.path.exists(package_path):
        raise FileNotFoundError(f"APK-файл {package_path} не найден.")
    
    # Заглушка: фиксированные зависимости для демонстрации.
    return {
        "package": ["libA", "libB"],
        "libA": ["libC"],
        "libB": ["libD", "libE"],
        "libC": [],
        "libD": ["libF"],
        "libE": [],
        "libF": [],
    }


def generate_dot(dependencies):
    """Создаёт представление графа зависимостей в формате DOT."""
    lines = ["digraph Dependencies {"]
    for package, deps in dependencies.items():
        for dep in deps:
            lines.append(f'    "{package}" -> "{dep}";')
    lines.append("}")
    return "\n".join(lines)


def save_dot_to_file(dot_content, output_path):
    """Сохраняет содержимое DOT в файл."""
    dot_path = Path(output_path).with_suffix(".dot")
    with open(dot_path, "w") as f:
        f.write(dot_content)
    print(f"Файл графа (DOT) сохранён: {dot_path}")
    return dot_path


def render_graph(dot_path, graphviz_path, output_path):
    """Выполняет рендеринг графа с помощью Graphviz."""
    png_path = Path(output_path).with_suffix(".png")
    try:
        subprocess.run([graphviz_path, "-Tpng", str(dot_path), "-o", str(png_path)], check=True)
        print(f"Граф успешно визуализирован: {png_path}")
    except FileNotFoundError:
        raise RuntimeError(f"Не удалось найти Graphviz по пути: {graphviz_path}")
    return png_path


def main(config_path):
    """Основной процесс выполнения."""
    print("Чтение конфигурационного файла...")
    config = read_config(config_path)
    
    print("Анализ зависимостей APK-пакета...")
    dependencies = parse_dependencies(config["package_path"], config["repository_url"])
    
    print("Генерация графа зависимостей (DOT)...")
    dot_content = generate_dot(dependencies)
    
    print("Сохранение графа в файл...")
    dot_path = save_dot_to_file(dot_content, config["output_path"])
    
    print("Визуализация графа с помощью Graphviz...")
    render_graph(dot_path, config["graphviz_path"], config["output_path"])
    
    print("Процесс завершён успешно!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Визуализация графа зависимостей APK-пакета.")
    parser.add_argument("config", help="Путь к конфигурационному файлу.")
    args = parser.parse_args()

    try:
        main(args.config)
    except Exception as e:
        print(f"Ошибка: {e}")
