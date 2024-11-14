import zipfile
import os
import json
import time
import xml.etree.ElementTree as ET


class ShellEmulator:
    def __init__(self, config_path):
        self.load_config(config_path)
        self.cwd = '/'  # Текущая рабочая директория
        self.history = []  # История команд
        self.output = []  # Список для хранения вывода
        self.load_virtual_fs()  # Загрузка виртуальной файловой системы
        self.current_directory = "/"

    def load_config(self, config_path):
        # Загрузка конфигурации из JSON файла
        with open(config_path, 'r') as f:
            config = json.load(f)
            self.zip_path = config['filesystem']['path']
            self.log_path = config['log']['path']

    def load_virtual_fs(self):
        # Открытие zip архива
        self.zip_file = zipfile.ZipFile(self.zip_path, 'r')
        self.files = self.zip_file.namelist()

    def log_action(self, action):
        # Логирование действия в XML файл
        try:
            tree = ET.parse(self.log_path)
            root = tree.getroot()
        except ET.ParseError:
            root = ET.Element("session")

        action_elem = ET.SubElement(root, "action", time=str(time.time()))
        action_elem.text = action

        tree = ET.ElementTree(root)
        tree.write(self.log_path)

    def execute_command(self, command):
        self.history.append(command)
        parts = command.split()

        if parts[0] == 'ls':
            self.ls()
        elif parts[0] == 'cd':
            if len(parts) > 1:
                self.cd(parts[1])
            else:
                self.show_output("Usage: cd <directory>")
        elif parts[0] == 'exit':
            self.exit_shell()
        elif parts[0] == 'tac':
            if len(parts) > 1:
                self.tac(parts[1])
            else:
                self.show_output("Usage: tac <file>")
        elif parts[0] == 'pwd':
            self.pwd()
        elif parts[0] == 'who':
            self.who()
        else:
            self.show_output(f"Command '{parts[0]}' not found")

    def ls(self):
        # Отображение содержимого текущей директории
        items = set()
        cwd_with_slash = self.cwd.rstrip('/') + '/'

        for file in self.files:
            if file.startswith(cwd_with_slash) and file != cwd_with_slash:
                relative_path = file[len(cwd_with_slash):].strip('/')
                if '/' in relative_path:
                    directory = relative_path.split('/')[0]
                    items.add(directory + '/')
                else:
                    items.add(relative_path)

        if items:
            self.show_output("\n".join(sorted(items)))
        else:
            self.show_output("Directory is empty")

        # Логирование команды
        self.log_action(f"ls in {self.cwd}")

    def cd(self, path):
        # Изменение текущей рабочей директории
        if path == '..':
            self.cwd = os.path.dirname(self.cwd.rstrip('/'))
            if not self.cwd:
                self.cwd = '/'
        else:
            new_path = os.path.join(self.cwd.rstrip('/'), path).lstrip('/')
            if any(file.startswith(new_path + '/') for file in self.files):
                self.cwd = new_path
                self.show_output(f"Changed directory to {self.cwd}")
            else:
                self.show_output(f"Directory '{path}' not found")

        # Логирование команды
        self.log_action(f"cd to {self.cwd}")

    def tac(self, filename):
        # Отображение содержимого файла в обратном порядке
        full_path = os.path.join(self.cwd, filename)
        if full_path in self.files:
            with self.zip_file.open(full_path) as f:
                lines = f.read().decode('utf-8').splitlines()
                reversed_lines = "\n".join(reversed(lines))
                self.show_output(reversed_lines)
        else:
            self.show_output(f"File '{filename}' not found")

        # Логирование команды
        self.log_action(f"tac {filename}")

    def pwd(self):
        # Отображение текущей директории
        self.show_output(self.cwd)

        # Логирование команды
        self.log_action("pwd")

    def who(self):
        # Отображение информации о текущем сеансе
        session_info = f"Computer Name: {self.computer_name}\nSession Time: {time.ctime()}"
        self.show_output(session_info)

        # Логирование команды
        self.log_action("who")

    def exit_shell(self):
        self.show_output("Exiting shell...")
        exit()

    def show_output(self, output):
        print(output)

    def get_output(self):
        return "\n".join(self.output)

    def clear_output(self):
        self.output = []


def main():
    # Запуск эмулятора с конфигурационным файлом
    shell = ShellEmulator('config.json')

    while True:
        # Ввод команды с клавиатуры
        command = input(f"{shell.cwd} $ ")
        if command.strip().lower() == "exit":
            shell.exit_shell()
        else:
            shell.execute_command(command)


if __name__ == '__main__':
    main()
