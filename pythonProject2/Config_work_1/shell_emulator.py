import os
import zipfile
import json
import xml.etree.ElementTree as ET
import shutil
from datetime import datetime

class XMLLogger:
    def __init__(self, log_path):
        self.log_path = log_path
        self.root = ET.Element("session")
    
    def log_command(self, command, output):
        command_element = ET.SubElement(self.root, "command")
        ET.SubElement(command_element, "name").text = command
        ET.SubElement(command_element, "timestamp").text = datetime.now().isoformat()
        ET.SubElement(command_element, "output").text = output
    
    def save(self):
        tree = ET.ElementTree(self.root)
        tree.write(self.log_path, encoding="utf-8", xml_declaration=True)

class ShellEmulator:
    def __init__(self, fs_root, logger):
        self.fs_root = fs_root
        self.current_dir = fs_root
        self.logger = logger
    
    def ls(self):
        contents = os.listdir(self.current_dir)
        output = "\n".join(contents)
        self.logger.log_command("ls", output)
        return output
    
    def cd(self, path):
        new_path = os.path.join(self.current_dir, path)
        if os.path.isdir(new_path):
            self.current_dir = new_path
            output = f"Changed directory to {new_path}"
        else:
            output = "Directory not found"
        self.logger.log_command("cd", output)
        return output
    
    def pwd(self):
        output = os.path.relpath(self.current_dir, self.fs_root)
        self.logger.log_command("pwd", output)
        return output
    
    def tac(self, filename):
        filepath = os.path.join(self.current_dir, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'r') as f:
                lines = f.readlines()
            output = "".join(lines[::-1])
        else:
            output = "File not found"
        self.logger.log_command("tac", output)
        return output
    
    def who(self):
        try:
            output = os.getlogin()
        except OSError:
            output = "Unknown user"
        self.logger.log_command("who", output)
        return output
    
    def exit(self):
        self.logger.log_command("exit", "Session ended")
        self.logger.save()
        return "Exiting shell emulator."

def load_config(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config['filesystem_path'], config['log_path']

def setup_virtual_filesystem(zip_path):
    if os.path.exists('vfs'):
        shutil.rmtree('vfs')
    os.makedirs('vfs')
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall('vfs')
    return 'vfs'

def run_shell_emulator(config_path):
    fs_path, log_path = load_config(config_path)
    fs_root = setup_virtual_filesystem(fs_path)
    logger = XMLLogger(log_path)
    emulator = ShellEmulator(fs_root, logger)
    
    print("Shell emulator started. Type 'exit' to quit.")
    while True:
        command = input("> ").strip()
        if command == "exit":
            print(emulator.exit())
            break
        elif command == "ls":
            print(emulator.ls())
        elif command.startswith("cd "):
            path = command.split(" ", 1)[1]
            print(emulator.cd(path))
        elif command == "pwd":
            print(emulator.pwd())
        elif command.startswith("tac "):
            filename = command.split(" ", 1)[1]
            print(emulator.tac(filename))
        elif command == "who":
            print(emulator.who())
        else:
            print("Command not found.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python shell_emulator.py <config_path>")
    else:
        run_shell_emulator(sys.argv[1])
