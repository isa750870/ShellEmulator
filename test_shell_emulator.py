import unittest
from io import StringIO
import sys
from emulator import Directory, File, ShellGUI, save_filesystem, build_filesystem



class TestShellCommands(unittest.TestCase):
    def setUp(self):
        # Создаем тестовую файловую систему
        self.root = Directory('/')
        self.dir1 = Directory('dir1', self.root)
        self.file1 = File('file1.txt', b'Hello, world!', self.dir1)
        self.root.add_child(self.dir1)
        self.dir1.add_child(self.file1)
        self.shell_gui = ShellGUI(self.root)

        # Подменяем вывод
        self.held_output = StringIO()
        sys.stdout = self.held_output

    def tearDown(self):
        # Возвращаем обычный вывод
        sys.stdout = sys.__stdout__

    def test_ls(self):
        # Тестируем команду ls
        self.shell_gui.execute_command('ls')
        output = self.held_output.getvalue().strip()
        self.assertEqual(output, '')

        self.held_output.truncate(0)  # Очищаем буфер вывода
        self.held_output.seek(0)

        self.shell_gui.execute_command('ls dir1')
        output = self.held_output.getvalue().strip()
        self.assertEqual(output, '')

        self.held_output.truncate(0)
        self.held_output.seek(0)

        self.shell_gui.execute_command('ls nonexistent_dir')
        output = self.held_output.getvalue().strip()
        self.assertEqual(output, '')

    def test_cd(self):
        # Тестируем команду cd
        self.shell_gui.execute_command('cd dir1')
        self.assertEqual(self.shell_gui.cwd, self.dir1)

        self.shell_gui.execute_command('cd ..')
        self.assertEqual(self.shell_gui.cwd, self.root)

        self.held_output.truncate(0)
        self.held_output.seek(0)

        self.shell_gui.execute_command('cd nonexistent_dir')
        output = self.held_output.getvalue().strip()
        self.assertEqual(output, "")

    def test_rm(self):
        # Тестируем команду rm

        self.held_output.truncate(0)
        self.held_output.seek(0)

        self.shell_gui.execute_command('rm nonexistent_file.txt')
        output = self.held_output.getvalue().strip()
        self.assertEqual(output, "")

        self.held_output.truncate(0)
        self.held_output.seek(0)

        self.shell_gui.execute_command('rm')
        output = self.held_output.getvalue().strip()
        self.assertEqual(output, "")

    def test_tree(self):
        # Тестируем команду tree
        self.shell_gui.execute_command('tree')
        output = self.held_output.getvalue().strip()
        self.assertEqual(output, '')

        self.held_output.truncate(0)
        self.held_output.seek(0)

        self.shell_gui.execute_command('tree nonexistent_dir')
        output = self.held_output.getvalue().strip()
        self.assertEqual(output, '')

if __name__ == '__main__':
    unittest.main()
