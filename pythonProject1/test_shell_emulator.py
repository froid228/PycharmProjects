from shell_emulator import ShellEmulator
import os

def test_shell_emulator():
    emulator = ShellEmulator('config.json')  # Загружаем эмулятор с конфигурационным файлом

    test_passed = 0
    total_tests = 12  # 2 теста на каждую из 6 команд

    # --- Test 1: ls - List files in the root directory ---
    print("Test 1: List files in the root directory")
    emulator.ls()
    expected_output = "\nhome/  etc/  tmp/"
    if emulator.get_output() == expected_output:
        test_passed += 1
    else:
        print(f"Failed: {emulator.get_output()}")

    # --- Test 2: ls - List files in home/user directory ---
    print("\nTest 2: List files in the home/user directory")
    emulator.cd('home/user')  # Перейти в директорию
    emulator.ls()
    expected_output = "document.txt  notes.txt"
    if emulator.get_output() == expected_output:
        test_passed += 1
    else:
        print(f"Failed: {emulator.get_output()}")

    # --- Test 3: cd - Change directory to home/user ---
    print("\nTest 3: Change directory to home/user")
    emulator.cd('home/user')  # Перейти в директорию
    if emulator.get_output() == "Changed directory to home/user":
        test_passed += 1
    else:
        print(f"Failed: {emulator.get_output()}")

    # --- Test 4: cd - Try to change to a non-existing directory ---
    print("\nTest 4: Try to change to a non-existing directory")
    emulator.cd('invalid_directory')  # Попытка перейти в несуществующую директорию
    if "Directory 'invalid_directory' not found" in emulator.get_output():
        test_passed += 1
    else:
        print(f"Failed: {emulator.get_output()}")

    # --- Test 5: rm - Remove an existing file ---
    print("\nTest 5: Remove an existing file")
    emulator.rm('home/user/document.txt')  # Удалить файл
    if "Removed file home/user/document.txt" in emulator.get_output():
        test_passed += 1
    else:
        print(f"Failed: {emulator.get_output()}")

    # --- Test 6: rm - Try to remove a non-existing file ---
    print("\nTest 6: Try to remove a non-existing file")
    emulator.rm('invalid_file.txt')  # Попытка удалить несуществующий файл
    if "File 'invalid_file.txt' not found" in emulator.get_output():
        test_passed += 1
    else:
        print(f"Failed: {emulator.get_output()}")

    # --- Test 7: tac - Show content of a file in reverse ---
    print("\nTest 7: Show content of home/user/notes.txt in reverse")
    emulator.tac('home/user/notes.txt')  # Показать содержимое в обратном порядке
    expected_output = "seton .s'eno"
    if emulator.get_output().startswith(expected_output):
        test_passed += 1
    else:
        print(f"Failed: {emulator.get_output()}")

    # --- Test 8: tac - Show content of tmp/temp_file.txt in reverse ---
    print("\nTest 8: Show content of tmp/temp_file.txt in reverse")
    emulator.tac('tmp/temp_file.txt')  # Показать содержимое в обратном порядке
    expected_output = "temf elif yraropmet"
    if emulator.get_output().startswith(expected_output):
        test_passed += 1
    else:
        print(f"Failed: {emulator.get_output()}")

    # --- Test 9: pwd - Show current directory ---
    print("\nTest 9: Show current directory (pwd)")
    emulator.pwd()
    if emulator.get_output() == "/":
        test_passed += 1
    else:
        print(f"Failed: {emulator.get_output()}")

    # --- Test 10: pwd - Show current directory after cd ---
    print("\nTest 10: Show current directory after cd to home/user")
    emulator.cd('home/user')  # Перейти в другую директорию
    emulator.pwd()
    if emulator.get_output() == "home/user":
        test_passed += 1
    else:
        print(f"Failed: {emulator.get_output()}")

    # --- Test 11: who - Show session information ---
    print("\nTest 11: Show session information (who)")
    emulator.who()
    if "Computer Name:" in emulator.get_output() and "Session Time:" in emulator.get_output():
        test_passed += 1
    else:
        print(f"Failed: {emulator.get_output()}")

    # --- Test 12: who - Show session information after commands ---
    print("\nTest 12: Show session information after executing commands (who)")
    emulator.ls()  # Выполнить команду для изменения состояния
    emulator.who()
    if "Computer Name:" in emulator.get_output() and "Session Time:" in emulator.get_output():
        test_passed += 1
    else:
        print(f"Failed: {emulator.get_output()}")

    # Результат
    print(f"\nAll {test_passed}/{total_tests} tests passed successfully!")

if __name__ == "__main__":
    test_shell_emulator()
