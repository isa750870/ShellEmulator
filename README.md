# ShellEmulator
Первое домашнее задание по Конфигурационному Управлению

## Постановка задания

### Задание №1
Разработать эмулятор для языка оболочки ОС. Необходимо сделать работу
эмулятора как можно более похожей на сеанс shell в UNIX-подобной ОС.
Эмулятор должен запускаться из реальной командной строки, а файл с
виртуальной файловой системой не нужно распаковывать у пользователя.
Эмулятор принимает образ виртуальной файловой системы в виде файла формата
tar. Эмулятор должен работать в режиме GUI.
Конфигурационный файл имеет формат xml и содержит:
- Путь к архиву виртуальной файловой системы.
- Путь к стартовому скрипту.

Стартовый скрипт служит для начального выполнения заданного списка
команд из файла.
Необходимо поддержать в эмуляторе команды ls, cd и exit, а также
следующие команды: rm, tree.
Все функции эмулятора должны быть покрыты тестами, а для каждой из
поддерживаемых команд необходимо написать 3 теста.

Для запуска ввести в консоль: 

```python emulator.py config.xml```

Для запуска тестов ввести в консоль: 

```python -m unittest test_shell_emulator.py```

## Важно!

Для работы программы необходимо поменть путь к директории проекта в файле config.xml
