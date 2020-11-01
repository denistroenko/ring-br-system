from classes import *
from baseapplib import *
import random
import os
import sys

# GLOBAL CONFIG
config = Config()

def set_config_defaults():
    global config
    # Главная секция
    config.settings['main'] = {}
    # Папка с архивами (куда складывать, чем управлять)
    config.settings['main']['ring_dir'] = '/mnt/ring'
    # Удаленная папка (Откуда брать)
    config.settings['main']['remote_dir'] = '/mnt/remote'
    # Секция кольца
    config.settings['ring'] = {}
    # Префикс имен файлов
    config.settings['ring']['prefix'] = 'ring_file_'
    # Количество объекток архивов для хранения
    config.settings['ring']['count'] = '30'
    # Срок хранения архивов в днях
    config.settings['ring']['time'] = '30'
    # Тип кольца архивов: count - по количеству, time - по давности,
    # count+time - по давности, но также и по количеству
    config.settings['ring']['type'] = 'count'


def print_settings():
    global config
    for key_section in config.settings:
        for key_setting in config.settings[key_section]:
            print('[{}] [{}] = {}'.format\
                  (key_section, key_setting,
                   config.settings[key_section][key_setting])
                 )


def print_title(message, border_simbol = "#"):
    os.system('clear')
    width = 90
    if len(border_simbol) * (width // len(border_simbol)) != width:
        width = len(border_simbol) * (width // len(border_simbol))
    print(border_simbol * (width // len(border_simbol)))
    for string in message:
        half1 = width // 2 - len(string) // 2 - len(border_simbol)
        half2 = width - (half1 + len(string)) - len(border_simbol) * 2
        print(border_simbol +
            ' ' * half1 +
            string +
            ' ' * half2 +
            border_simbol)
    print(border_simbol * (width // len(border_simbol)))


def print_file_line(year, month, day, time, file_name, file_size,
               difference,
               color_year= '\033[30m\033[47m',
               color_month = '\033[30m\033[47m',
               color_day = '\033[30m\033[47m',
               color_time = '\033[37m\033[40m',
               color_file_name = '\033[34m\033[40m',
               color_file_size = '\033[37m\033[40m',
               color_difference = '\033[32m\033[40m',
               color_default = '\033[37m\033[40m',
               date_separator = '-'):

    # Default string formats for data
    year = "{:04d}".format(year)
    month = "{:02d}".format(month)
    day = "{:02d}".format(day)
    # file_size = "{: 10d}".format(file_size)

    line = f'{color_year}{year}{date_separator}'
    line += f'{color_month}{month}{date_separator}'
    line += f'{color_day}{day}'
    line += f'{color_default} {color_time}{time}'
    line += f'{color_default} {color_file_name}{file_name}'
    line += f'{color_default} {color_file_size}{file_size}'
    line += f'{color_default} {color_difference}{difference}%'
    if difference > 100:
        line += f'{color_default} {color_difference}(+{difference-100}%)'
    else:
        line += f'{color_default} {color_difference}({difference-100}%)'

    line += f'{color_default} '

    print(line)


def test():
    files_list = []
    for i in range(10):
        year = random.randint(2000, 2020)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        hour = random.randint(1, 23)
        minute = random.randint(1, 59)
        second = random.randint(1, 59)
        size = random.randint(1000, 1000)
        if i == 4: size = 970
        if i == 5: size = 950
        if i ==7: size = 900
        if i ==8: size = 1000
        if i ==9: size = 200
        file = RingFile('', '')
        file.set_date_modify(year, month, day, hour, minute, second)
        file.set_size(size)
        files_list.append(file)
    prev_size = 0
    for file in files_list:
        date = file.get_modify_date()
        time = date.time()
        size = file.get_size()

        if prev_size == 0:
            prev_size = size
        difference = size / prev_size

        if difference > 0.9 and difference < 1.1:
            print_file_line(date.year, date.month, date.day, time,
                   'filename', size, round(difference * 100))
        elif difference > 0.8 and difference < 1.2:
            print_file_line(date.year, date.month, date.day, time,
                   'filename', size, round(difference * 100),
                    color_difference = '\033[31m')
        else:
            print_file_line(date.year, date.month, date.day, time,
                   'filename', size, round(difference * 100),
                    color_difference = '\033[37m\033[41m')
        prev_size = size
    config.write_file()
    os.system('cat ./config_exp')


def print_help():
    print('--help\t\t\t- выдает это сообщение помощи по командам')
    print('--settings -s\t\t- вывод текущих настроек программы')
    print('--analyze -a\t\t- ???')
    print('--test -t\t\t- ???')


def analyze():
    print()


def main():
    # Set default settings in global config
    set_config_defaults()

    # If "--help" in args command line, then print help and exit
    for param in sys.argv:
        if param == '--help':
            print_help()
            exit()

    # Print message and print all settings in global config
    message = ['Algorithm Computers', 'a-computers.ru', 'dev@a-computers.ru',
                '', '"Ring"', 'Утилита управления архивными файлами']
    print_title(message, '*')
    print()

    # Read config file
    print('Чтение файла настроек...')
    config.read_file()

    # Read args command line
    for param in sys.argv:
        if param == '--settings' or param == '-s':
            print('Текущие настройки программы:')
            print_settings()
            print()
        if param == '--test' or param == '-t':
            test()
        if param == '--analyze' or param == '-a':
            analyze()

main()
