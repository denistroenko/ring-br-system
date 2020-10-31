from classes import *
import random

def print_line(year, month, day, time, file_name, file_size,
               color_year= '\033[30m\033[47m',
               color_month = '\033[30m\033[47m',
               color_day = '\033[30m\033[47m',
               color_time = '\033[37m\033[40m',
               color_file_name = '\033[34m\033[40m',
               color_file_size = '\033[32m\033[40m',
               color_default = '\033[37m\033[40m',
               date_separator = '-'):

    # Default string formats for data
    year = "{:04d}".format(year)
    month = "{:02d}".format(month)
    day = "{:02d}".format(day)

    line = f'{color_year}{year}{date_separator}'
    line += f'{color_month}{month}{date_separator}'
    line += f'{color_day}{day}'
    line += f'{color_default} {color_time}{time}'
    line += f'{color_default} {color_file_name}{file_name}'
    line += f'{color_default} {color_file_size}{file_size}'
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
        size = random.randint(1000, 999999999)

        file = RingFile('', '')
        file.set_date_modify(year, month, day, hour, minute, second)
        file.set_size(size)

        files_list.append(file)

    for file in files_list:
        date = file.get_modify_date()
        time = date.time()
        size = file.get_size()

        print_line(date.year, date.month, date.day, time,
                   'filename', size)

test()
