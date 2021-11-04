"""
Config module for read|write|load|export settings
"""
import sys
import os
import inspect


def get_script_dir(follow_symlinks=True):
    """
    Возвращает путь к скрипту __main__ (папку)
    """
    if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return '{}/'.format(os.path.dirname(path))


#need !!! pep8
class Section():
    def __init__(self, section_dict):
        for key in section_dict:
            setattr(self, key, section_dict[key])


# need edit for pep8!!!!!!!!!!!!!!!!!!!!!!!!
class Config:

    def __init__(self):
        self.settings = {}

    def __getattr__(self, attr):
        try:
            return getattr(self, attr)
        except:
            section_dict = self.get_section_dict(attr)
            section = Section(section_dict)
            return section

    def __str__(self) -> str:
        out_str = ''
        for key_section in self.settings:
            for key_setting in self.settings[key_section]:
                out_str += '[{}] {} = {}\n'.format\
                    (key_section, key_setting,
                    self.settings[key_section][key_setting])
        return out_str

    def read_file(self,
                  full_path: str = '{}config'.format(get_script_dir()),
                  separator: str = '=',
                  comment: str = '#',
                  section_start: str = '[',
                  section_end: str = ']'):
        ok = True

        try:
            with open(full_path, 'r') as file:
                # считать все строки файла в список
                lines = file.readlines()  # грязный список

                # удаляем переводы строк, табы заменяем пробелами
                for index in range(len(lines)):
                    lines[index] = lines[index].replace('\n', '')
                    lines[index] = lines[index].replace('\t', ' ')

                # удаляем строки, начинающиеся с комментария, если это
                # не пустые строки
                for line in lines:
                    if len(line) > 0:
                        if line[0] == comment:
                            lines.remove(line)

                # удаляем правую часть строки после комментария
                for index in range(len(lines)):
                    if comment in lines[index]:
                        lines[index] = lines[index].split(comment)[0]

                # удаляем пустые строки из списка
                while "" in lines:
                    lines.remove("")

                # проходим по списку,
                # если встречаем разделитель, делим элемент на 2,
                # и загружаем key:value в словарь
                section = "main"  # Секция по-умолчанию
                for line in lines:
                    if section_start in line and section_end in line:
                        section = line[1:-1].strip()
                    if separator in line:
                        # разделить с макс. кол-вом делений: 1
                        settings_pair = line.split(separator, maxsplit=1)
                        # Удаляем пробелы в начале и конце
                        settings_pair[0] = settings_pair[0].strip()
                        settings_pair[1] = settings_pair[1].strip()

                        self.set(section=section,
                                 setting=settings_pair[0],
                                 value=settings_pair[1],
                                 )
        except FileNotFoundError:
            print('ОШИБКА! Файл', full_path, 'не найден!')
            ok = False

        return ok

    def write_file(self,
                   full_path: str = get_script_dir() + 'config_exp',
                   separator: str = '=',
                   comment: str = '#',
                   section_start: str = '[',
                   section_end: str = ']'):

        ok = True

        try:
            with open(full_path, 'w') as file:
                for section in self.settings:
                    tab = 25 - len(section)
                    if tab < 2:
                        tab = 2
                    file.write(section_start +
                               section +
                               section_end +
                               ' ' * tab + comment + ' Секция параметров ' +
                               section + '\n\n')
                    for setting in self.settings[section]:
                        if len(self.settings[section][setting]) > 0:
                            tab = 24 - (len(setting) +
                                        len(self.settings[section][setting]))
                            if tab < 2:
                                tab = 2

                            file.write(setting + ' ' + separator + ' ' +
                                    self.settings[section][setting] +
                                    ' ' * tab + comment +
                                    ' Значение параметра ' +
                                    setting + '\n')
                    file.write('\n\n')

        except FileNotFoundError:
            print('ОШИБКА! Файл', full_path, 'не найден!')
            ok = False

        return ok

    def clear(self):
        self.settings = {}

    def get(self, section: str, setting: str) -> str:
        return str(self.settings[section][setting])

    def get_section_dict(self, section) -> dict:
        return self.settings[section]

    def set(self, section: str, setting: str, value: str):
        if section not in self.settings.keys():
            self.settings[section] = {}
        self.settings[section][setting] = str(value)
