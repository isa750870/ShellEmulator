import unittest
import os
import tarfile
from emulator import ShellEmulator

class TestShellEmulator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Открываем архив виртуальной файловой системы
        cls.filesystem_tar = r"C:\Users\Kirill\Documents\Shell\virtual_filesystem.tar"
        cls.emulator = ShellEmulator(r"C:\Users\Kirill\Documents\Shell\config.xml")
        cls.emulator.extract_filesystem()  # Извлечение содержимого архива
        cls.emulator.current_dir = cls.emulator.temp_dir  # Установка текущей директории

    @classmethod
    def tearDownClass(cls):
        cls.emulator.cleanup()  # Очистка временной директории

    def test_ls(self):
        expected_output = "dir1  dir2"  # Ожидаемый вывод для команды ls
        output = self.emulator.cmd_ls([])
        self.assertIn(expected_output, output)

    def test_cd_success(self):
        self.emulator.cmd_cd(['virtual_filesystem'])  # Переход в директорию dir1
        self.assertEqual(self.emulator.current_dir, os.path.join(self.emulator.temp_dir, 'virtual_filesystem'))

    def test_cd_failure(self):
        output = self.emulator.cmd_cd(['non_existing_dir'])
        self.assertIn("Нет такой директории:", output)

    def test_rm_file(self):
        # Удаляем file1.txt и проверяем, что он больше не существует
        self.emulator.cmd_rm(['dir1/file1.txt'])
        self.assertFalse(os.path.exists(os.path.join(self.emulator.current_dir, 'dir1/file1.txt')))

    def test_rm_directory(self):
        self.emulator.cmd_rm(['dir2'])  # Удаляем dir2
        self.assertFalse(os.path.exists(os.path.join(self.emulator.current_dir, 'dir2')))

    def test_tree(self):
        expected_output = "dir1"  # Проверка структуры
        output = self.emulator.cmd_tree([])
        self.assertIn(expected_output, output)

if __name__ == "__main__":
    unittest.main()