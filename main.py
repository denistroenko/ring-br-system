from classes import *
from baseapplib import *

# GLOBAL objects
console = Console()
config = Config()
ring = Ring()

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

    # Солько показывать файлов в кольце (0 - все)
    config.set('show', 'show_last', '10')
    # Проценты отклонения от и до, в зеленой зоне и в красной,
    config.set('show', 'green_min', '-5')
    config.set('show', 'green_max', '5')
    config.set('show', 'red_min', '-20')
    config.set('show', 'red_max', '20')
    # Показывать исключенные из ring_dir файлы
    config.set('show', 'show_excluded', 'yes')


def print_settings():
    global config
    print(config)


def print_error(error: str, stop_program: bool = False):
    print('\033[31m{}'.format(error), '\033[37m\033[40m')
    if stop_program:
        sys.exit()


def print_file_line(year, month, day, time, file_name, file_size,
                    difference, show_plus_space: bool,
               color_date = '\033[30m\033[47m',
               color_time = '\033[37m\033[40m',
               color_file_name = '\033[34m\033[40m',
               color_file_size = '\033[537m\033[40m',
               color_difference = '\033[32m\033[40m',
               color_default = '\033[37m\033[40m',
               date_separator = '-'):

    # Default string formats for data
    year = "{:04d}".format(year)
    month = "{:02d}".format(month)
    day = "{:02d}".format(day)

    file_size = human_space(file_size)

    line = f'{color_date}{year}{date_separator}{month}{date_separator}{day}'
    line += f'{color_default} {color_time}{time}'
    line += f'{color_default} {color_file_name}{file_name}'
    line += f'{color_default} {color_file_size}{file_size}'
    if difference > 0:
        line += f'{color_default} {color_difference}+{difference}%'
    elif difference < 0:
        line += f'{color_default} {color_difference}{difference}%'

    if show_plus_space:
        line += f'{color_default} {color_difference}+{file_size}'


    line += f'{color_default} '

    print(line)


def human_space(bytes: int) -> str:
    if bytes >= 1024 ** 3:
        result = str('{} Gb'.format(round(bytes/1024**3, 1)))
    elif bytes >= 1024 ** 2:
        result = str('{} Mb'.format(round(bytes/1024**2, 1)))
    elif bytes >= 1024:
        result = str('{} Kb'.format(round(bytes/1024), 1))
    else:
        result = str('{} bytes'.format(bytes))
    return result


def show(short: bool):
    global ring
    global config

    message = ['SHOW RING MODE']
    console.print_title(message, '~', 50)

    files = ring.get_files()
    if len(files) == 0:
        print_error('В ring-каталоге нет ни одного ring-файла.', show)
    if short:
        start = int(config.get('show', 'show_last'))
        short_list = files[-start:]
        if len (short_list) < len (files):
            short_count = len(files) - len(short_list)
            files = short_list
            print('...', ' (не показаны предыдущие ', short_count, ')',
                  sep = '')
    green_min = round(float(config.get('show', 'green_min')), 2)
    green_max = round(float(config.get('show', 'green_max')), 2)
    red_min = round(float(config.get('show', 'red_min')), 2)
    red_max = round(float(config.get('show', 'red_max')),2 )

    last_file_date = files[-1].get_date_modify()
    today_date = datetime.datetime.now()
    if last_file_date.date() == today_date.date():
        last_file_date_is_today = True
    else:
        last_file_date_is_today = False

    prev_size = -1
    for file in files:
        file_name = file.get_file_name()
        size = file.get_size()
        date = file.get_date_modify()
        time = date.time()

        if prev_size == -1:
            prev_size = size

        if prev_size == 0:
            ratio = 0
            show_plus_space = True
            color_difference = '\033[37m\033[41m'

        else:
            ratio = round(size / prev_size * 100 - 100, 2)
            show_plus_space = False
            color_difference = '\033[32m\033[40m'

        if files[-1] == file and not last_file_date_is_today:
            color_date = '\033[37m\033[41m'
        elif files[-1] == file and last_file_date_is_today:
            color_date = '\033[37m\033[42m'
        else:
            color_date = '\033[30m\033[47m'

        if ratio >= green_min and ratio <= green_max:
            print_file_line(date.year, date.month, date.day, time,
                            file_name, size, ratio, show_plus_space,
                            color_difference = color_difference,
                            color_date = color_date)
        elif ratio >= red_min and ratio <= red_max:
            print_file_line(date.year, date.month, date.day, time,
                            file_name, size, ratio, show_plus_space,
                            color_difference = '\033[31m',
                            color_date = color_date)
        else:
            print_file_line(date.year, date.month, date.day, time,
                            file_name, size, ratio, show_plus_space,
                            color_difference = '\033[37m\033[41m',
                            color_date = color_date)
        prev_size = size
        total_space = ring.get_total_space()
    print('Всего файлов: ', ring.get_total_files(), '\tЗанято места: ',
         human_space(total_space), sep = '')


def load_ring_files():
    path = config.get('main', 'ring_dir')
    prefix = config.get('ring', 'prefix')
    if config.get('show', 'show_excluded').lower == 'yes':
        show_excluded = True
    else:
        show_excluded = False
    ring.clear()
    try:
        ring.load(path, prefix, show_excluded)
    except FileNotFoundError:
        print_error('Не найден ring-каталог: {}'.format(path), True)


def print_help():
    print('--help\t\t\t- выдает это сообщение помощи по командам')
    print('--settings -s\t\t- вывод текущих настроек программы')
    print('--test -t\t\t- ???')


def ring_cut():
    global ring
    global console
    ok = True

    message = 'CUT MODE'
    console.print_title(message, '~', 50)

    cut_type = config.get('ring', 'type')
    if cut_type == 'count':
        try:
            count = int(config.get('ring', 'count'))
            ring.cut_by_count(count)
        except:
            print_error('Неверная настройка [ring] count в файле config.')
    elif cut_type == 'time':
        ring.cut_by_time
    elif cut_type == 'space':
        try:
            gigabytes = round(float(config.get('ring', 'space')), 2)
            ring.cut_by_space(gigabytes)
        except:
            print_error('Неверная настройка [ring] space в файле config.')
    else:
        print_error('Неизвестный режим работы кольца: {}.'.format(
                    cut_type), True)

    return ok


def sort_ring_files():
    global ring
    ring.sort()


def fix_config():
    # Фиксим: последний символ в пути к папке должен быть '/'
    ring_dir = config.get('main', 'ring_dir')
    if ring_dir[-1] != '/':
        ring_dir = ring_dir + '/'
        config.set('main', 'ring_dir', ring_dir)

    # Фиксим: последний символ в пути к папке должен быть '/'
    remote_dir = config.get('main', 'remote_dir')
    if remote_dir[-1] != '/':
        remote_dir = remote_dir + '/'
        config.set('main', 'remote_dir', remote_dir)


def main():
    global console
    args = console.get_args()

    if '--help' in args:
        print_help()
        sys.exit()

    # Set default settings in global config
    set_config_defaults()

    # Print message and print all settings in global config
    message = ['Algorithm Computers', 'a-computers.ru', 'dev@a-computers.ru',
                '', '"Ring"', 'Утилита управления архивными файлами']
    console.print_title(message, '*', 50)
    print()

    # Read config file
    config.read_file()

    fix_config()

    # Load ring files (objects)
    load_ring_files()

    # Sort ring files (list)
    sort_ring_files()

    # Read args command line
    if '--settings' in args or '-s' in args:
        print('Текущие настройки программы:')
        print_settings()
        print()
    if '--test' in args or '-t' in args:
        pass
    if 'cut' in args:
        ring_cut()
    if 'show' in args:
        if int(config.get('show', 'show_last')) > 0:
            show(True)
        else:
            show(False)

main()
