"""
Config module for get|set|load|export settings
"""


class Section():
    """
    Section class.
    Init need dict 'section dict' ({key:value, ...}),
    create namespace, available in object.<key>
    object.<key> return value
    """
    def __init__(self, section_dict):
        for key in section_dict:
            setattr(self, key, section_dict[key])

    def __getattr__(self, attr):
        """
        If exist attr, returned attr.
        Else returned section
        """
        try:
            return getattr(self, attr)
        except Exception:
            return None


# need edit for pep8!!!!!!!!!!!!!!!!!!!!!!!!
class Config:
    """
    Class of global config.
    """
    def __init__(self):
        """
        Init. Set defaults.
        """
        self.settings = {}

    def __getattr__(self, attr):
        """
        If exist attr, returned attr.
        Else returned section
        """
        try:
            return getattr(self, attr)
        except Exception:
            section_dict = self.get_section_dict(attr)
            section = Section(section_dict)
            return section

    def __str__(self) -> str:
        """
        Return lines of settings in text format.
        """
        out_str = ''
        for key_section in self.settings:
            for key_setting in self.settings[key_section]:
                out_str += '[{}] {} = {}\n'.format(
                        key_section,
                        key_setting,
                        self.settings[key_section][key_setting],
                        )
        return out_str

    def read_file(self,
                  config_file: str,
                  separator: str = '=',
                  comment: str = '#',
                  section_start: str = '[',
                  section_end: str = ']',
                  except_if_error: bool = False,
                  out: object = print,
                  ) -> bool:
        ok = True

        try:
            with open(config_file, 'r') as file:
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
            ok = False

            file_not_found_msg = f'Файл {config_file} не найден!'
            file_is_dir_msg = f'{config_file} - это каталог!'

            if except_if_error:
                raise FileNotFoundError(file_not_found_msg)
            else:
                out(file_not_found_msg)

        except IsADirectoryError:
            ok = False

            if except_if_error:
                raise IsADirectoryError(file_is_dir_msg)
            else:
                out(file_is_dir_msg)

        return ok

    def write_file(self,
                   config_file: str,
                   separator: str = '=',
                   comment: str = '#',
                   section_start: str = '[',
                   section_end: str = ']'):

        ok = True

        try:
            with open(config_file, 'w') as file:
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
            print('ОШИБКА! Файл', config_file, 'не найден!')
            ok = False

        return ok

    def clear(self):
        self.settings = {}

    def get(self, section: str, setting: str) -> str:
        return str(self.settings[section][setting])

    def get_section_dict(self, section) -> dict:
        return self.settings[section]

    def set(self, section: str, setting: str, value: str):
        """
        Create or rewrited section, setting, value
        """
        # if 'section' not exist, create it
        if section not in self.settings.keys():
            self.settings[section] = {}
        self.settings[section][setting] = str(value)
