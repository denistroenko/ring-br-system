from classes import *
from baseapplib import *
import random
import sys

# GLOBAL CONFIG
config = Config()
ring_files_list = []

def set_config_defaults():
    global config

    # Папка с архивами (куда складывать, чем управлять)
    config.set('main', 'ring_dir', '/mnt/ring/')  # Критический
    # Удаленная папка (Откуда брать)
    config.set('main', 'remote_dir', '/mnt/remote/')  # Критический

    # Префикс имен файлов
    config.set('ring', 'prefix', 'ring_archive_')
    # Количество объекток архивов для хранения
    config.set('ring', 'count', '30')
    # Срок хранения архивов в днях
    config.set('ring', 'time', '30')
    # Макс. занимаемое пространство для папки с архивами
    config.set('ring', 'space', '200')
    # Тип кольца архивов: (count|time|space)
    config.set('ring', 'type', 'count')

    # Слать ли отчет администратору (yes|no)
    config.set('email', 'send_admin_email', 'no')
    # admin email
    config.set('email', 'admin_email', '')
    # Слать ли отчет конечному пользователю
    config.set('email', 'send_user_email', 'no')
    # user email
    config.set('email', 'user_email', '')


def print_settings():
    global config
    print(config)


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
    global ring_files_list
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
        ring_files_list.append(file)
    prev_size = 0
    for file in ring_files_list:
        date = file.get_date_modify()
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
    system('cat ./config_exp')


def load_ring_files():
    global ring_files_list
    ring_files_list = []


def print_help():
    print('--help\t\t\t- выдает это сообщение помощи по командам')
    print('--settings -s\t\t- вывод текущих настроек программы')
    print('--test -t\t\t- ???')


def ring_cut(cut_type: str):
    ok = True
    return ok


def ring_cut_count(count: int):
    ok = True
    return ok


def ring_cut_time(days: int):
    ok = True
    return ok


def ring_cut_space(gigabytes: int):
    ok = True
    return ok


def sort_ring_files_list():
    global ring_files_list
    new_list = sorted(ring_files_list, key=lambda file: file.get_date_modify())
    ring_files_list = new_list


def main():
    console = Console()
    args = console.get_args()

    if '--help' in args:
        print_help()
        exit()

    # Set default settings in global config
    set_config_defaults()

    # Print message and print all settings in global config
    message = ['Algorithm Computers', 'a-computers.ru', 'dev@a-computers.ru',
                '', '"Ring"', 'Утилита управления архивными файлами']
    console.print_title(message, '*')
    print()

    # Read config file
    print('Чтение файла настроек...')
    config.read_file()

    # Load ring files (objects)
    load_ring_files()

    # Sort ring files (list)
    sort_ring_files_list()

    # Read args command line
    if '--settings' in args or '-s' in args:
        print('Текущие настройки программы:')
        print_settings()
        print()
    if '--test' in args or '-t' in args:
        test()



main()
