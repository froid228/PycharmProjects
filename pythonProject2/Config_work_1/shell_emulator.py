import os
import zipfile
import json
import xml.etree.ElementTree as ET
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

class ZipShellEmulator:
    def __init__(self, zip_path, logger):
        self.zip_path = zip_path
        self.current_dir = ""
        self.logger = logger
        self.zip_file = zipfile.ZipFile(zip_path, 'r')
    
    def ls(self):
        contents = [
            name[len(self.current_dir):].split('/')[0]
            for name in self.zip_file.namelist()
            if name.startswith(self.current_dir) and name != self.current_dir
        ]
        contents = sorted(set(contents))  # Remove duplicates and sort
        output = "\n".join(contents)
        self.logger.log_command("ls", output)
        return output
    
    def cd(self, path):
        new_dir = os.path.normpath(os.path.join(self.current_dir, path)) + '/'
        if any(name.startswith(new_dir) for name in self.zip_file.namelist()):
            self.current_dir = new_dir
            output = f"Changed directory to {new_dir}"
        else:
            output = "Directory not found"
        self.logger.log_command("cd", output)
        return output
    
    def pwd(self):
        output = "/" + self.current_dir.strip('/')
        self.logger.log_command("pwd", output)
        return output
    
    def tac(self, filename):
        filepath = os.path.normpath(self.current_dir + filename)
        try:
            with self.zip_file.open(filepath, 'r') as f:
                lines = f.readlines()
            output = "".join(line.decode('utf-8')[::-1] for line in lines[::-1])
        except KeyError:
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
        self.zip_file.close()
        return "Exiting shell emulator."

def load_config(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config['filesystem_path'], config['log_path']

def run_shell_emulator(config_path):
    fs_path, log_path = load_config(config_path)
    logger = XMLLogger(log_path)
    emulator = ZipShellEmulator(fs_path, logger)
    
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
