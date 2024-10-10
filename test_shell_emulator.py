import unittest
from io import StringIO
import sys
from emulator import *

class TestShellCommands(unittest.TestCase):

    def setUp(self):
        # Создаем виртуальную файловую систему для тестов
        self.root = Directory('/')
        self.dir1 = Directory('dir1')
        self.dir2 = Directory('dir2')
        self.file1 = File('file1.txt', b'content of file1', self.dir1)
        self.root.add_child(self.dir1)
        self.root.add_child(self.dir2)
        self.dir1.add_child(self.file1)
        self.shell = ShellGUI(self.root)

    def test_ls(self):
        # Проверяем команду ls без аргументов
        self.shell.ls_command([])
        output = self.get_output()
        self.assertIn('dir1', output)
        self.assertIn('dir2', output)

        # Проверяем ls с правильным путем
        self.shell.ls_command(['dir1'])
        output = self.get_output()
        self.assertIn('file1.txt', output)

        # Проверяем ls с неправильным путем
        self.shell.ls_command(['nonexistent'])
        output = self.get_output()
        self.assertIn('nonexistent: Not a directory', output)

    def test_cd(self):
        # Проверяем cd на существующий каталог
        self.shell.cd_command(['dir1'])
        self.assertEqual(self.shell.cwd, self.dir1)

        # Проверяем cd на несуществующий каталог
        self.shell.cd_command(['nonexistent'])
        output = self.get_output()
        self.assertIn('cd: nonexistent: No such file or directory', output)

        # Проверяем cd на выход из каталога
        self.shell.cd_command(['..'])
        self.assertEqual(self.shell.cwd, self.root)

    def test_rm(self):
        # Проверяем rm на существующий файл
        self.shell.rm_command(['dir1/file1.txt'])
        output = self.get_output()
        self.assertNotIn('file1.txt', self.dir1.children)

        # Проверяем rm на несуществующий файл
        self.shell.rm_command(['dir1/file1.txt'])
        output = self.get_output()
        self.assertIn("rm: cannot remove 'dir1/file1.txt': No such file or directory", output)

        # Проверяем rm без аргументов
        self.shell.rm_command([])
        output = self.get_output()
        self.assertIn("rm: missing operand", output)

    def test_tree(self):
        # Проверяем команду tree для корневого каталога
        self.shell.tree_command([])
        output = self.get_output()
        self.assertIn('dir1', output)
        self.assertIn('dir2', output)

        # Проверяем tree для существующего каталога
        self.shell.tree_command(['dir1'])
        output = self.get_output()
        self.assertIn('file1.txt', output)

        # Проверяем tree для несуществующего каталога
        self.shell.tree_command(['nonexistent'])
        output = self.get_output()
        self.assertIn('nonexistent: Not a directory', output)

    def get_output(self):
        return self.shell.text.get('1.0', 'end').strip()

if __name__ == '__main__':
    unittest.main()
