import os
import tarfile
import tkinter as tk
import xml.etree.ElementTree as ET
import tempfile
import shutil
import subprocess
from gui import ShellGUI

class ShellEmulator:
    def __init__(self, config_path):
        self.load_config(config_path)
        self.extract_filesystem()
        self.current_dir = self.temp_dir  # Начальная директория
        self.commands = {
            'ls': self.cmd_ls,
            'cd': self.cmd_cd,
            'exit': self.cmd_exit,
            'rm': self.cmd_rm,
            'tree': self.cmd_tree
        }
        self.is_running = True

    def load_config(self, config_path):
        tree = ET.parse(config_path)
        root = tree.getroot()
        self.filesystem_tar = root.find('filesystem').text
        self.start_script = root.find('start_script').text

    def extract_filesystem(self):
        self.temp_dir = tempfile.mkdtemp()
        with tarfile.open(self.filesystem_tar, 'r') as tar:
            tar.extractall(path=self.temp_dir)

    def run_start_script(self):
        if os.path.exists(self.start_script):
            with open(self.start_script, 'r') as script:
                for line in script:
                    command = line.strip()
                    if command:
                        response = self.execute_command(command)
                        if response:
                            self.gui.append_output(response + "\n")
        else:
            self.gui.append_output("Стартовый скрипт не найден.\n")

    def execute_command(self, command_line):
        parts = command_line.split()
        if not parts:
            return ""
        cmd = parts[0]
        args = parts[1:]
        if cmd in self.commands:
            return self.commands[cmd](args)
        else:
            return f"Неизвестная команда: {cmd}"

    # Команды
    def cmd_ls(self, args):
        try:
            items = os.listdir(self.current_dir)
            return '  '.join(items)
        except Exception as e:
            return str(e)

    def cmd_cd(self, args):
        if not args:
            return "Использование: cd <путь>"
        path = args[0]
        new_path = os.path.abspath(os.path.join(self.current_dir, path))
        if os.path.isdir(new_path):
            self.current_dir = new_path
            return ""
        else:
            return f"Нет такой директории: {path}"

    def cmd_exit(self, args):
        self.is_running = False
        self.gui.root.quit()
        return ""

    def cmd_rm(self, args):
        if not args:
            return "Использование: rm <файл/директория>"
        path = args[0]
        target = os.path.abspath(os.path.join(self.current_dir, path))
        try:
            if os.path.isfile(target):
                os.remove(target)
                return f"Файл удалён: {path}"
            elif os.path.isdir(target):
                shutil.rmtree(target)
                return f"Директория удалёна: {path}"
            else:
                return f"Нет такого файла или директории: {path}"
        except Exception as e:
            return str(e)

    def cmd_tree(self, args):
        tree_str = self.generate_tree(self.current_dir)
        return tree_str

    def generate_tree(self, directory, prefix=""):
        tree = ""
        entries = os.listdir(directory)
        entries.sort()
        for index, entry in enumerate(entries):
            path = os.path.join(directory, entry)
            connector = "└── " if index == len(entries) -1 else "├── "
            tree += prefix + connector + entry + "\n"
            if os.path.isdir(path):
                extension = "    " if index == len(entries) -1 else "│   "
                tree += self.generate_tree(path, prefix + extension)
        return tree

    def start_gui(self):
        root = tk.Tk()
        self.gui = ShellGUI(root, self.process_command)
        # Запуск стартового скрипта в отдельном потоке, чтобы не блокировать GUI
        self.run_start_script()
        self.gui.start()

    def process_command(self, command_line):
        return self.execute_command(command_line)

    def cleanup(self):
        shutil.rmtree(self.temp_dir)

    def run(self):
        try:
            self.start_gui()
        finally:
            self.cleanup()

if __name__ == "__main__":
    config_path = r"C:\Users\Kirill\Documents\Shell\config.xml"
    emulator = ShellEmulator(config_path)
    emulator.run()