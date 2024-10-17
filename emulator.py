import sys
import tarfile
import xml.etree.ElementTree as ET
import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import io

# Классы для представления файловой системы
class FileSystemEntry:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent

class File(FileSystemEntry):
    def __init__(self, name, data, parent=None):
        super().__init__(name, parent)
        self.data = data

class Directory(FileSystemEntry):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.children = {}

    def add_child(self, entry):
        self.children[entry.name] = entry
        entry.parent = self

# Функция для чтения конфигурационного файла
def read_config(config_file):
    tree = ET.parse(config_file)
    root = tree.getroot()
    filesystem_path = root.find('filesystem').text
    startup_script_path = root.find('startup_script').text
    return filesystem_path, startup_script_path

# Функция для построения файловой системы из tar-архива
def build_filesystem(tar_file_path):
    root_dir = Directory('/')
    tar = tarfile.open(tar_file_path, 'r')
    for member in tar.getmembers():
        path_parts = member.name.strip('/').split('/')
        current_dir = root_dir
        for part in path_parts[:-1]:
            if part not in current_dir.children:
                new_dir = Directory(part, current_dir)
                current_dir.add_child(new_dir)
            current_dir = current_dir.children[part]
        if member.isdir():
            if path_parts[-1] not in current_dir.children:
                new_dir = Directory(path_parts[-1], current_dir)
                current_dir.add_child(new_dir)
        else:
            file_content = tar.extractfile(member).read() if member.size > 0 else b''
            new_file = File(path_parts[-1], file_content, current_dir)
            current_dir.add_child(new_file)
    tar.close()
    return root_dir

# Функция для сохранения файловой системы в tar-архив
def save_filesystem(root_dir, tar_file_path):
    tar = tarfile.open(tar_file_path, 'w')
    def add_entry(tar, entry, path):
        if isinstance(entry, Directory):
            # Убедимся, что путь заканчивается на '/'
            if not path.endswith('/'):
                path += '/'
            info = tarfile.TarInfo(name=path.strip('/'))
            info.type = tarfile.DIRTYPE
            tar.addfile(info)
            for child in entry.children.values():
                add_entry(tar, child, path + child.name)
        elif isinstance(entry, File):
            data = entry.data
            info = tarfile.TarInfo(name=path.strip('/'))
            info.size = len(data)
            tar.addfile(info, fileobj=io.BytesIO(data))
    for child in root_dir.children.values():
        add_entry(tar, child, child.name)
    tar.close()

# Класс для GUI эмулятора shell
class ShellGUI:
    def __init__(self, root_dir, startup_script_path=None, filesystem_path=None):
        self.root_dir = root_dir
        self.filesystem_path = filesystem_path
        self.root = tk.Tk()
        self.root.title("Эмулятор Shell")
        self.text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, bg='black', fg='white')
        self.text.pack(expand=True, fill='both')
        self.text.bind('<Return>', self.on_enter)
        self.text.bind('<BackSpace>', self.on_backspace)
        self.text.bind('<Key>', self.on_key)
        self.text.focus_set()
        self.cwd = root_dir
        self.update_prompt()
        self.display_prompt()
        if startup_script_path:
            self.run_startup_script(startup_script_path)
        self.previous_command = ""

    def display_prompt(self):
        self.text.insert(tk.END, self.prompt)
        self.text.mark_set('insert', 'end')
        self.text.see('insert')

    def on_enter(self, event):
        line_start = self.text.search(self.prompt, 'insert linestart')
        command = self.text.get(line_start + f'+{len(self.prompt)}c', 'insert').strip()
        if command != self.previous_command:
            self.text.insert(tk.END, '\n')
            self.previous_command = command
            self.execute_command(command)
            self.display_prompt()
        return 'break'

    def on_backspace(self, event):
        prompt_index = self.text.search(self.prompt, 'insert linestart')
        if self.text.compare('insert', '==', prompt_index + f'+{len(self.prompt)}c'):
            return 'break'

    def on_key(self, event):
        prompt_index = self.text.search(self.prompt, 'insert linestart')
        if self.text.compare('insert', '<', prompt_index + f'+{len(self.prompt)}c'):
            self.text.mark_set('insert', 'end')
            return 'break'

    def execute_command(self, command):
        args = command.strip().split()
        if not args:
            return
        cmd = args[0]
        if cmd == 'ls':
            self.ls_command(args[1:])
        elif cmd == 'cd':
            self.cd_command(args[1:])
        elif cmd == 'exit':
            self.root.quit()
        elif cmd == 'rm':
            self.rm_command(args[1:])
        elif cmd == 'tree':
            self.tree_command(args[1:])
        else:
            self.text.insert(tk.END, f"{cmd}: Команда не найдена\n")

    def ls_command(self, args):
        directory = self.cwd
        if args:
            path = args[0]
            directory = self.resolve_path(path)
            if directory is None or not isinstance(directory, Directory):
                self.text.insert(tk.END, f"{path}: Не является директорией или не существует\n")
                return
        names = sorted(directory.children.keys())
        self.text.insert(tk.END, ' '.join(names) + '\n')

    def cd_command(self, args):
        if not args:
            self.cwd = self.root_dir
            self.update_prompt()
            return
        path = args[0]
        new_dir = self.resolve_path(path)
        if new_dir and isinstance(new_dir, Directory):
            self.cwd = new_dir
            self.update_prompt()
        else:
            self.text.insert(tk.END, f"cd: {path}: Не является файлом или директорией\n")

    def rm_command(self, args):
        if not args:
            self.text.insert(tk.END, "rm: неверный ввод\n")
            return
        path = args[0]
        parent_dir, name = self.resolve_parent(path)
        if parent_dir and name in parent_dir.children:
            del parent_dir.children[name]
            # Сохраняем обновленную файловую систему в архив
            save_filesystem(self.root_dir, self.filesystem_path)
        else:
            self.text.insert(tk.END, f"rm: Нельзя удалить '{path}': Не является файлом или директорией\n")

    def tree_command(self, args):
        directory = self.cwd
        if args:
            path = args[0]
            directory = self.resolve_path(path)
            if not isinstance(directory, Directory):
                self.text.insert(tk.END, f"{path}: Не является директорией\n")
                return
        output = []
        self.build_tree(directory, '', output)
        self.text.insert(tk.END, '\n'.join(output) + '\n')

    def build_tree(self, directory, prefix, output):
        output.append(f"{prefix}{directory.name}")
        for name, entry in sorted(directory.children.items()):
            if isinstance(entry, Directory):
                self.build_tree(entry, prefix + '    ', output)
            else:
                output.append(f"{prefix}    {entry.name}")

    def resolve_path(self, path):
        if path.startswith('/'):
            current = self.root_dir
            parts = path.strip('/').split('/')
        else:
            current = self.cwd
            parts = path.strip().split('/')
        for part in parts:
            if part == '.' or part == '':
                continue
            elif part == '..':
                if current.parent:
                    current = current.parent
            elif part in current.children:
                current = current.children[part]
            else:
                return None
        return current

    def resolve_parent(self, path):
        if path.startswith('/'):
            current = self.root_dir
            parts = path.strip('/').split('/')
        else:
            current = self.cwd
            parts = path.strip().split('/')
        for part in parts[:-1]:
            if part == '.' or part == '':
                continue
            elif part == '..':
                if current.parent:
                    current = current.parent
            elif part in current.children:
                current = current.children[part]
            else:
                return None, None
        return current, parts[-1] if parts else ''

    def update_prompt(self):
        path = self.get_cwd_path()
        self.prompt = f"{path}$ "

    def get_cwd_path(self):
        path = ''
        dirs = []
        current = self.cwd
        while current and current.name != '/':
            dirs.append(current.name)
            current = current.parent
        path = '/' + '/'.join(reversed(dirs))
        if path == '':
            path = '/'
        return path

    def run_startup_script(self, script_path):
        try:
            with open(script_path, 'r') as f:
                commands = f.readlines()
            for cmd in commands:
                cmd = cmd.strip()
                if cmd:
                    self.text.insert(tk.END, cmd + '\n')
                    self.execute_command(cmd)
        except FileNotFoundError:
            self.text.insert(tk.END, f"Стартовый скрипт не найден: {script_path}\n")

# Главная часть программы
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование: python emulator.py <config_file>")
        sys.exit(1)
    config_file = sys.argv[1]
    filesystem_path, startup_script_path = read_config(config_file)
    root_dir = build_filesystem(filesystem_path)
    shell_gui = ShellGUI(root_dir, startup_script_path, filesystem_path)
    shell_gui.root.mainloop()
