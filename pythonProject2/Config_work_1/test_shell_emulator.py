# test_shell_emulator.py

import os
import zipfile
import json
import xml.etree.ElementTree as ET
import shutil
from datetime import datetime
import tempfile

# Import classes and functions from shell_emulator.py
from shell_emulator import (
    XMLLogger,
    ShellEmulator,
    load_config,
    setup_virtual_filesystem
)

# --------------------- XMLLogger Tests ---------------------

def test_xml_logger_log_command():
    print("Testing XMLLogger.log_command...")

    # Test 1: Log a simple command
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as tmp:
        log_path = tmp.name

    logger = XMLLogger(log_path)
    logger.log_command("echo", "Hello World")
    logger.save()  # Ensure the log is saved before parsing

    tree = ET.parse(log_path)
    root = tree.getroot()
    commands = root.findall('command')
    assert len(commands) == 1, "Should have one command logged."
    assert commands[0].find('name').text == "echo", "Command name should be 'echo'."
    assert commands[0].find('output').text == "Hello World", "Command output should be 'Hello World'."
    os.remove(log_path)
    print("Test 1 passed.")

    # Test 2: Log multiple commands
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as tmp:
        log_path = tmp.name

    logger = XMLLogger(log_path)
    logger.log_command("ls", "file1\nfile2")
    logger.log_command("pwd", "/home/user")
    logger.save()

    tree = ET.parse(log_path)
    root = tree.getroot()
    commands = root.findall('command')
    assert len(commands) == 2, "Should have two commands logged."
    assert commands[1].find('name').text == "pwd", "Second command name should be 'pwd'."
    assert commands[1].find('output').text == "/home/user", "Second command output should be '/home/user'."
    os.remove(log_path)
    print("Test 2 passed.")

def test_xml_logger_save():
    print("Testing XMLLogger.save...")

    # Test 1: Save with one command
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as tmp:
        log_path = tmp.name

    logger = XMLLogger(log_path)
    logger.log_command("whoami", "user")
    logger.save()
    tree = ET.parse(log_path)
    root = tree.getroot()
    assert root.tag == "session", "Root tag should be 'session'."
    commands = root.findall('command')
    assert len(commands) == 1, "Should have one command saved."
    os.remove(log_path)
    print("Test 1 passed.")

    # Test 2: Save with multiple commands
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as tmp:
        log_path = tmp.name

    logger = XMLLogger(log_path)
    logger.log_command("pwd", "/home/user")
    logger.log_command("ls", "file1\nfile2")
    logger.save()
    tree = ET.parse(log_path)
    root = tree.getroot()
    commands = root.findall('command')
    assert len(commands) == 2, "Should have two commands saved."
    os.remove(log_path)
    print("Test 2 passed.")

# --------------------- ShellEmulator Tests ---------------------

def test_shell_emulator_ls():
    print("Testing ShellEmulator.ls...")

    # Setup temporary filesystem
    with tempfile.TemporaryDirectory() as fs_root:
        os.makedirs(os.path.join(fs_root, "dir1"))
        with open(os.path.join(fs_root, "file1.txt"), 'w') as f:
            f.write("Content1")
        logger = XMLLogger(os.path.join(fs_root, "log.xml"))
        emulator = ShellEmulator(fs_root, logger)

        # Test 1: List contents in root
        output = emulator.ls()
        expected = {"dir1", "file1.txt"}
        output_set = set(output.split('\n'))
        assert output_set == expected, f"ls output mismatch. Expected {expected}, got {output_set}."
        print("Test 1 passed.")

        # Test 2: List contents in empty directory
        emulator.cd("dir1")
        output = emulator.ls()
        expected = set()
        output_set = set(output.split('\n')) if output else set()
        assert output_set == expected, "ls in empty directory should return empty set."
        print("Test 2 passed.")

def test_shell_emulator_cd():
    print("Testing ShellEmulator.cd...")

    # Setup temporary filesystem
    with tempfile.TemporaryDirectory() as fs_root:
        os.makedirs(os.path.join(fs_root, "dir1"))
        logger = XMLLogger(os.path.join(fs_root, "log.xml"))
        emulator = ShellEmulator(fs_root, logger)

        # Test 1: Change to existing directory
        output = emulator.cd("dir1")
        expected = os.path.join(fs_root, "dir1")
        assert emulator.current_dir == expected, "Current directory should be dir1."
        assert output == f"Changed directory to {expected}", "cd output mismatch."
        print("Test 1 passed.")

        # Test 2: Attempt to change to non-existing directory
        output = emulator.cd("nonexistent")
        assert output == "Directory not found", "Should return 'Directory not found'."
        assert emulator.current_dir == expected, "Current directory should remain unchanged."
        print("Test 2 passed.")

def test_shell_emulator_pwd():
    print("Testing ShellEmulator.pwd...")

    # Setup temporary filesystem
    with tempfile.TemporaryDirectory() as fs_root:
        os.makedirs(os.path.join(fs_root, "dir1", "subdir"))
        logger = XMLLogger(os.path.join(fs_root, "log.xml"))
        emulator = ShellEmulator(fs_root, logger)

        # Test 1: pwd in root
        output = emulator.pwd()
        expected = "."
        assert output == expected, "pwd in root should return '.'."
        print("Test 1 passed.")

        # Test 2: pwd in subdirectory
        emulator.cd("dir1")
        emulator.cd("subdir")
        output = emulator.pwd()
        # Normalize paths for cross-platform compatibility
        normalized_output = output.replace('\\', '/')
        assert normalized_output == "dir1/subdir", f"pwd should return 'dir1/subdir', got '{output}'."
        print("Test 2 passed.")

def test_shell_emulator_tac():
    print("Testing ShellEmulator.tac...")

    # Setup temporary filesystem
    with tempfile.TemporaryDirectory() as fs_root:
        file_path = os.path.join(fs_root, "file.txt")
        with open(file_path, 'w') as f:
            f.write("Line1\nLine2\nLine3\n")
        logger = XMLLogger(os.path.join(fs_root, "log.xml"))
        emulator = ShellEmulator(fs_root, logger)

        # Test 1: tac on existing file
        output = emulator.tac("file.txt")
        expected = "Line3\nLine2\nLine1\n"
        assert output == expected, f"tac output mismatch. Expected '{expected}', got '{output}'."
        print("Test 1 passed.")

        # Test 2: tac on non-existing file
        output = emulator.tac("nonexistent.txt")
        expected = "File not found"
        assert output == expected, "tac should return 'File not found' for missing file."
        print("Test 2 passed.")

def test_shell_emulator_who():
    print("Testing ShellEmulator.who...")

    # Setup temporary filesystem
    with tempfile.TemporaryDirectory() as fs_root:
        logger = XMLLogger(os.path.join(fs_root, "log.xml"))
        emulator = ShellEmulator(fs_root, logger)

        # Test 1: who returns the current user
        try:
            expected = os.getlogin()
        except OSError:
            expected = "Unknown user"
        output = emulator.who()
        assert output == expected or expected == "Unknown user", "who output mismatch."
        print("Test 1 passed.")

        # Test 2: Simulate os.getlogin failure
        original_getlogin = os.getlogin
        try:
            # Monkey patch os.getlogin to raise OSError
            os.getlogin = lambda: (_ for _ in ()).throw(OSError)
            output = emulator.who()
            assert output == "Unknown user", "who should return 'Unknown user' when os.getlogin fails."
            print("Test 2 passed.")
        finally:
            os.getlogin = original_getlogin

def test_shell_emulator_exit():
    print("Testing ShellEmulator.exit...")

    # Setup temporary filesystem
    with tempfile.TemporaryDirectory() as fs_root:
        log_path = os.path.join(fs_root, "log.xml")
        logger = XMLLogger(log_path)
        emulator = ShellEmulator(fs_root, logger)

        # Test: Exit logs the exit command and saves the log
        exit_message = emulator.exit()
        assert exit_message == "Exiting shell emulator.", "Exit message mismatch."

        # Parse the log and verify commands
        tree = ET.parse(log_path)
        root = tree.getroot()
        commands = root.findall('command')
        assert len(commands) == 1, "Should have one command logged (exit)."
        assert commands[0].find('name').text == "exit", "Only command should be 'exit'."
        assert commands[0].find('output').text == "Session ended", "Exit command output mismatch."
        print("Test passed.")

# --------------------- load_config Tests ---------------------

def test_load_config():
    print("Testing load_config...")

    # Test 1: Valid config
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as tmp:
        config_path = tmp.name
        config = {
            "filesystem_path": "vfs.zip",
            "log_path": "log.xml"
        }
        json.dump(config, tmp)
    fs_path, log_path = load_config(config_path)
    assert fs_path == "vfs.zip", "filesystem_path should be 'vfs.zip'."
    assert log_path == "log.xml", "log_path should be 'log.xml'."
    os.remove(config_path)
    print("Test 1 passed.")

    # Test 2: Missing keys
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as tmp:
        config_path = tmp.name
        config = {
            "filesystem_path": "vfs.zip"
            # Missing 'log_path'
        }
        json.dump(config, tmp)
    try:
        fs_path, log_path = load_config(config_path)
        assert False, "Should have raised KeyError for missing 'log_path'."
    except KeyError:
        print("Test 2 passed.")
    finally:
        os.remove(config_path)

# --------------------- setup_virtual_filesystem Tests ---------------------

def test_setup_virtual_filesystem():
    print("Testing setup_virtual_filesystem...")

    # Test 1: Valid zip extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "test.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.writestr("file1.txt", "Content1")
            zipf.writestr("dir1/file2.txt", "Content2")

        fs_root = setup_virtual_filesystem(zip_path)
        assert os.path.exists(fs_root), "Filesystem root should exist."
        assert os.path.isfile(os.path.join(fs_root, "file1.txt")), "file1.txt should exist."
        assert os.path.isfile(os.path.join(fs_root, "dir1", "file2.txt")), "dir1/file2.txt should exist."
        shutil.rmtree(fs_root)
        print("Test 1 passed.")

    # Test 2: Invalid zip file
    with tempfile.TemporaryDirectory() as temp_dir:
        invalid_zip_path = os.path.join(temp_dir, "invalid.zip")
        with open(invalid_zip_path, 'w') as f:
            f.write("Not a zip file")
        try:
            setup_virtual_filesystem(invalid_zip_path)
            assert False, "Should have raised a zipfile.BadZipFile exception."
        except zipfile.BadZipFile:
            print("Test 2 passed.")

# --------------------- Running All Tests ---------------------

if __name__ == "__main__":
    test_xml_logger_log_command()
    test_xml_logger_save()
    test_shell_emulator_ls()
    test_shell_emulator_cd()
    test_shell_emulator_pwd()
    test_shell_emulator_tac()
    test_shell_emulator_who()
    test_shell_emulator_exit()  # Only exit test is present
    test_load_config()
    test_setup_virtual_filesystem()
    print("All tests completed successfully.")
