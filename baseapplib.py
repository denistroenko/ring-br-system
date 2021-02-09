
# version 0.0.16

# imports
import random
import smtplib
from email.mime.text import MIMEText
import os
import inspect
import sys


def get_script_dir(follow_symlinks=True):
    if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return '{}/'.format(os.path.dirname(path))


def human_space(bytes: int) -> str:
    if bytes >= 1024 ** 3:
        result = str('{}G'.format(round(bytes/1024**3, 1)))
    elif bytes >= 1024 ** 2:
        result = str('{}M'.format(round(bytes/1024**2, 1)))
    elif bytes >= 1024:
        result = str('{}K'.format(round(bytes/1024), 1))
    else:
        result = str('{}b'.format(bytes))
    return result


class PasswordGenerator:

    def __init__(self):
        self.use_special_symbols = False
        self.password_len = 12
        self.curent_password = ""
        self.get_new_password()

    def __str__(self):
        return \
            "Это класс 'Генератор Паролей'.\n" + \
            "Функция get_new_password() " + \
            "генерирует пароль указанной длины, " + \
            "равной атрибуту password_len.\n" + \
            "Атрибут use_special_symbols " + \
            "определяет, использовать ли при генерации специальные " + \
            "символы.\nГенерация ВСЕГДА возвращает " + \
            "пароль, состоящий из РАВНОГО количества частей:\n" + \
            "цифры/буквы/БУКВЫ/опционально-спец.символы"

    def get_new_password(self):
        # Даем списки, из которых будет генерироваться пароль
        list_of_chars = list("qwertyuiopasdfghjklzxcvbnm")
        list_of_CHARS = list("QWERTYUIOPASDFGHJKLZXCVBNM")
        list_of_numbers = list("1234567890")
        list_of_symbols = list("""~!@#$%^&*()[]{};:"'<>,.""")

        if self.use_special_symbols:
            # Распределяем доли пароля как четверть от его длины
            # на каждый список (букв, БУКВ, цифр и символов)
            count_of_chars = int(self.password_len / 4)
            count_of_CHARS = int(self.password_len / 4)
            count_of_numbers = int(self.password_len / 4)
            count_of_symbols = self.password_len - \
                (count_of_chars + count_of_CHARS + count_of_numbers)
        else:
            count_of_CHARS = int(self.password_len / 3)
            count_of_numbers = int(self.password_len / 3)
            count_of_chars = \
                self.password_len - (count_of_CHARS + count_of_numbers)
            count_of_symbols = 0

        # Если нужная доля пароля превышает кол-во элементов списка этой доли,
        # то умножим список на ......
        if len(list_of_numbers) < count_of_numbers:
            list_of_numbers *= \
                int(count_of_numbers / len(list_of_numbers) + 1)
        if len(list_of_CHARS) < count_of_CHARS:
            list_of_CHARS *= \
                int((count_of_CHARS / len(list_of_CHARS)) + 1)
        if len(list_of_numbers) < count_of_numbers:
            list_of_numbers *= \
                int((count_of_numbers / len(list_of_numbers)) + 1)
        if len(list_of_symbols) < count_of_symbols:
            list_of_symbols *= \
                int((count_of_symbols / len(list_of_symbols)) + 1)

        # Перетасовываем элементы списка
        random.shuffle(list_of_chars)
        random.shuffle(list_of_CHARS)
        random.shuffle(list_of_numbers)
        random.shuffle(list_of_symbols)

        # Обрезаем списки
        list_of_chars = list_of_chars[:count_of_chars]
        list_of_CHARS = list_of_CHARS[:count_of_CHARS]
        list_of_numbers = list_of_numbers[:count_of_numbers]
        if self.use_special_symbols:
            list_of_symbols = list_of_symbols[:count_of_symbols]

        # Соединяем списки
        main_list = list_of_chars + list_of_CHARS + list_of_numbers
        if self.use_special_symbols:
            main_list += list_of_symbols

        # Перетасовываем элементы списка
        random.shuffle(main_list)

        # Возвращаем значение (строку)
        # Превращаем список в строку ("" - разделитель)
        self.curent_password = "".join(main_list)
        return self.curent_password


class EmailSender:

    def __init__(self):
        self.__host = ''
        self.__login = ''
        self.__password = ''
        self.__from = ''
        self.__use_ssl = None
        self.__port = 0

    def configure(self, smtp_hostname: str, login: str, password: str,
                 from_address: str, use_ssl: bool = True, port: int = 465):
        self.__host = smtp_hostname
        self.__login = login
        self.__password = password
        self.__from = from_address
        self.__use_ssl = use_ssl
        self.__port = port

    def send_email(self, to_address: str, subject: str, message: str,
                   use_html_format: bool = False):

        if use_html_format:
            msg = MIMEText(message, "html", "utf8")
        else:
            msg = MIMEText(message, "plain", "utf8")

        msg['Subject'] = subject
        msg['From'] = self.__from
        msg['To'] = to_address

        if self.__use_ssl:
            server = smtplib.SMTP_SSL(self.__host, self.__port)
        else:
            server = smtplib.SMTP(self.__host)

        server.login(self.__login, self.__password)
        server.sendmail(self.__from, to_address, msg.as_string())
        server.quit()


class HtmlLetter:

    def __init__(self, background_color: str = '#fff',
                 color: str = '#333', font_size: int = 14):

        self.__background_color = background_color
        self.__color = color
        self.__font_size = font_size
        self.__html_letter = '<html>\n\t<body style="' + \
            'background-color: {}; ' + \
            'color: {}; ' + \
            'font-size: {}px; ' + \
            '">\n{}\n' + '\t</body>\n</html>'
        self.__body = ''

    def get_letter(self):

        html_letter = \
            self.__html_letter.format(self.__background_color,
                                      self.__color,
                                      str(self.__font_size),
                                      self.__body)
        return html_letter

    def append(self,
            text: str = '',
            tag_type: str = 'div',
            weight: int = 0,
            color: str = '',
            font_size: int = 0,
            border: bool = False,
            width: str = '100%'):

        text_block = '\t\t'
        text_block += '<' + tag_type + ' style="'
        if weight > 0:
            text_block += 'font-weight: ' + str(weight) + '; '
        if color != '':
            text_block += 'color: ' + color + '; '
        if font_size > 0:
            text_block += 'font-size: ' + str(font_size) + 'px; '
        if border:
            text_block += 'border: 1px solid ' + color + '; '
        text_block += 'width: ' + width + '; '
        text_block += '">'
        if text != '':
            text_block += text
        else:
            text_block += '<br>'
        text_block += '</' + tag_type + '>\n'

        self.__body += text_block

    def reset(self):

        self.__body = ''


class Config:

    def __init__(self):
        self.settings = {}

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

                # удаляем пробелы, табы и переводы строк
                for index in range(len(lines)):
                    lines[index] = lines[index].replace(' ', '')
                    lines[index] = lines[index].replace('\n', '')
                    lines[index] = lines[index].replace('\t', '')

                # удаляем строки, начинающиеся с комментария, если это
                # не пустые строки
                for line in lines:
                    if len(line) > 0:
                        if line[0] == comment:
                            lines.remove(line)

                # удаляем правую час ть строки после комментария
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
                        section = line[1:-1]
                    if separator in line:
                        settings_pair = line.split(separator)
                        # Работать только в том случае, если
                        # separator один на строку
                        if len(settings_pair) == 2:
                            self.set(section,
                                     settings_pair[0], settings_pair[1])
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


class Console:

    def __init__(self):
        self.__args_list = []
        self.__args_list = sys.argv[1:]

    def get_args(self) -> list:
        result = []
        for arg in self.__args_list:
            if arg[0:2] == '--':
                result.append('--{}'.format(arg[2:]))
            elif arg[0:1] == '-':
                for liter in arg[1:]:
                    result.append('-{}'.format(liter))
            else:
                result.append(arg)
        return result

    def print_title(self, title: list, border_simbol: str = "#",
                    width: int = 40, space_before: bool = True,
                    space_after: bool = True):
        if type(title) != list:
            title = [str(title), ]
        if len(border_simbol) * (width // len(border_simbol)) != width:
            width = len(border_simbol) * (width // len(border_simbol))

        if space_before:
            print()

        print(border_simbol * (width // len(border_simbol)))
        for string in title:
            half1 = width // 2 - len(string) // 2 - len(border_simbol)
            half2 = width - (half1 + len(string)) - len(border_simbol) * 2
            print(border_simbol +
                ' ' * half1 +
                string +
                ' ' * half2 +
                border_simbol)
        print(border_simbol * (width // len(border_simbol)))

        if space_after:
            print()

    def clear_screen(self):
        os.system('clear')

    def print(
        self,
        msg: str = '',
        color: str = 'white',
        bg_color: str = 'black',
        effect: str = '0',
        end: str = '\n',
        flush: bool = False,
    ):
        colors = {
            'black': '\033[30m',
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m',
            'purple': '\033[35m',
            'turquoise': '\033[36m',
            'white': '\033[37m',
            '0': '\033[30m',
            '1': '\033[31m',
            '2': '\033[32m',
            '3': '\033[33m',
            '4': '\033[34m',
            '5': '\033[35m',
            '6': '\033[36m',
            '7': '\033[37m',
        }
        bg_colors = {
            'black': '\033[40m',
            'red': '\033[41m',
            'green': '\033[42m',
            'yellow': '\033[43m',
            'blue': '\033[44m',
            'purple': '\033[45m',
            'turquoise': '\033[46m',
            'white': '\033[47m',
            '0': '\033[40m',
            '1': '\033[41m',
            '2': '\033[42m',
            '3': '\033[43m',
            '4': '\033[44m',
            '5': '\033[45m',
            '6': '\033[46m',
            '7': '\033[47m',
        }

        effects = {
            '0': '\033[0m',
            '1': '\033[1m',
            '2': '\033[2m',
            '3': '\033[3m',
            '4': '\033[4m',
            '5': '\033[5m',
            '6': '\033[6m',
            '7': '\033[7m',
        }

        default_colors = '\033[0m\033[37m\033[40m'

        if not color in colors:
            color = 'white'
        if not bg_color in colors:
            bg_color = 'black'
        if not effect in effects:
            effect = '0'

        print(
            f'{effects[effect]}{colors[color]}{bg_colors[bg_color]}{msg}{default_colors}',
            flush = flush,
            end = end,
        )
