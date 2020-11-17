from classes import *
from baseapplib import *
import glob

# GLOBAL
VERSION = '0.0.1'
console = Console()
config = Config()
ring = Ring()
APP_DIR = get_script_dir()
CONFIG_FILE = '{}config'.format(APP_DIR)


def set_config_defaults():
    global config

    # Папка с архивами (куда складывать, чем управлять)
    config.set('ring', 'dir', '/mnt/ring/')  # Критический
    # Префикс имен файлов
    config.set('ring', 'prefix', '')
    # Количество объектов архивов для хранения
    config.set('ring', 'count', '30')
    # Срок хранения архивов в днях
    config.set('ring', 'age', '180')
    # Макс. занимаемое пространство для папки с архивами в гигабайтах
    config.set('ring', 'space', '200')
    # Тип кольца архивов: (count|age|space)
    config.set('ring', 'type', 'count')
    # Показывать исключенные из ring_dir файлы
    config.set('ring', 'show_excluded', 'no')

    # Слать ли отчет администратору (yes|no)
    config.set('email', 'send_admin_email', 'no')
    # admin email
    config.set('email', 'admin_email', '')
    # Слать ли отчет конечному пользователю
    config.set('email', 'send_user_email', 'no')
    # user email
    config.set('email', 'user_email', '')

    # Солько показывать файлов в кольце (0 - все)
    config.set('show', 'show_last', '15')
    # Проценты отклонения от и до, в зеленой зоне и в красной
    config.set('show', 'green_min', '-5')
    config.set('show', 'green_max', '5')
    config.set('show', 'red_min', '-20')
    config.set('show', 'red_max', '20')
    # "Зеленый" срок хранения последнего архивного файла в ring-каталоге
    config.set('show', 'green_age', '7')

    # Тип remote-подключения к source (ftp/smb/none)
    config.set('remote_source', 'type', 'none')
    config.set('remote_source', 'mount', '')
    config.set('remote_source', 'host', '')
    config.set('remote_source', 'user', '')
    config.set('remote_source', 'password', '')

    # Тип remote-подключения к ring (ftp/smb/none)
    config.set('remote_ring', 'type', 'none')
    config.set('remote_ring', 'mount', '')
    config.set('remote_ring', 'host', '')
    config.set('remote_ring', 'user', '')
    config.set('remote_ring', 'password', '')

    # Удаленные объекты (брать по маске). Беруться все элементы {take-files}
    # config.set('take-files', 'files', '*')  # Критический по усл.
    # Режим получения файлов для архивирования (copy/move/none)
    config.set('take', 'mode', 'copy')  # Критический по условию
    # Брать только сегодняшние файлы
    config.set('take', 'only_today', 'no')

    # config.set('take-dirs', '', '')  # Критический по условию

    config.set('archive', 'deflated', 'yes')
    config.set('archive', 'date_format', 'YYYY-MM-DD_WW_hh:mm:ss')


def print_settings():
    global config
    print(config)


def print_error(error: str, stop_program: bool = False):
    print('\033[31m{}'.format(error), '\033[37m\033[40m')
    if stop_program:
        sys.exit()


def print_file_line(number,
                    year, month, day, time, age, file_name, file_size,
                    difference, show_plus_space: bool,
               color_date = '\033[30m\033[47m',
               color_time = '\033[37m\033[40m',
               color_age = '\033[30m\033[47m',
               color_file_name = '\033[34m\033[40m',
               color_file_size = '\033[537m\033[40m',
               color_difference = '\033[32m\033[40m',
               color_default = '\033[37m\033[40m',
               date_separator = '-'):

    # Default string formats for data
    number = "{:03d}".format(number)
    year = "{:04d}".format(year)
    month = "{:02d}".format(month)
    day = "{:02d}".format(day)
    age = "{:3d}d".format(age)

    file_size = human_space(file_size)
    while len(file_size) < 6:
        file_size += ' '

    line = f'{color_default}{number} '
    line += f'{color_date}{year}{date_separator}{month}{date_separator}{day}'
    line += f'{color_default} {color_time}{time}'
    line += f'{color_default} {color_age}{age}'
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


def show_mode():
    ok = True
    global ring
    global config


    if int(config.get('show', 'show_last')) > 0:
        short = True
    else:
        short = False

    message = ['SHOW RING MODE']
    console.print_title(message, '~', 55)

    files = ring.get_files()
    file_no = 0
    if len(files) == 0:
        print_error('В ring-каталоге нет ни одного ring-файла.', False)
        ok = False
        return ok
    if short:
        start = int(config.get('show', 'show_last'))
        short_list = files[-start:]
        if len(short_list) < len(files):
            short_count = len(files) - len(short_list)
            file_no = short_count
            files = short_list
            print('...', ' (не показаны предыдущие ', short_count, ')',
                  sep = '')
    green_min = round(float(config.get('show', 'green_min')), 2)
    green_max = round(float(config.get('show', 'green_max')), 2)
    red_min = round(float(config.get('show', 'red_min')), 2)
    red_max = round(float(config.get('show', 'red_max')),2 )

    green_age = int(config.get('show', 'green_age'))

    prev_size = -1
    for file in files:
        file_no += 1

        file_name = file.get_file_name()
        size = file.get_size()
        date = file.get_date_modify()
        time = date.time()
        age = file.get_age()

        if len(file_name) > 26:
            word_left = file_name[0:18]
            word_right = file_name[-4:]
            file_name = f'{word_left}[..]{word_right}'

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

        if files[-1] == file and \
                age > green_age:
            color_date = '\033[37m\033[41m'
            color_age = '\033[37m\033[41m'
        elif files[-1] == file and \
                age <= green_age:
            color_date = '\033[30m\033[42m'
            color_age = '\033[30m\033[42m'
        else:
            color_date = '\033[30m\033[47m'
            color_age = '\033[30m\033[47m'

        if ratio >= green_min and ratio <= green_max:
            print_file_line(file_no,
                            date.year, date.month, date.day, time, age,
                            file_name, size, ratio, show_plus_space,
                            color_difference = color_difference,
                            color_age = color_age,
                            color_date = color_date)
        elif ratio >= red_min and ratio <= red_max:
            print_file_line(file_no,
                            date.year, date.month, date.day, time, age,
                            file_name, size, ratio, show_plus_space,
                            color_difference = '\033[31m',
                            color_age = color_age,
                            color_date = color_date)
        else:
            print_file_line(file_no,
                            date.year, date.month, date.day, time, age,
                            file_name, size, ratio, show_plus_space,
                            color_difference = '\033[37m\033[41m',
                            color_age = color_age,
                            color_date = color_date)
        prev_size = size
        total_space = ring.get_total_space()
    print('Всего файлов: ', ring.get_total_files(), '; Занято места: ',
         human_space(total_space), sep = '')


def show_content_zip_file(file_index: int = -1):
    global ring

    files_list = ring.get_files()
    try:
        file = files_list[file_index]
    except IndexError:
        print_error('Нет файла с таким номером!', True)
    full_path = file.get_full_path()

    print('Читаю файл {} ...'.format(full_path))
    ok, content = file.zip_content()
    if ok:
        print(content)
    else:
        print_error(content, False)


def test_zip_file(file_index: int = -1):
    global ring

    files_list = ring.get_files()
    try:
        file = files_list[file_index]
    except IndexError:
        print_error('Нет файла с таким номером!', True)

    full_path = file.get_full_path()

    print('Тестирую файл {} ...'.format(full_path))
    ok, test_result = file.zip_test()
    if ok:
        print(test_result)
    else:
        print_error(test_result, False)


def cut_bad_mode():
    global ring
    total_deleted_files = 0

    message = 'CUT-BAD MODE'
    console.print_title(message, '~', 55)

    files_list = ring.get_files()
    for file in files_list:
        full_path = file.get_full_path()

        print('Тестирую файл {} ...'.format(full_path))
        test_ok, test_result = file.zip_test()
        if test_ok:
            print(test_result)
        else:
            print_error(test_result, False)
            file.delete_from_disk()
            total_deleted_files += 1
    print('Всего удалено файлов:', total_deleted_files)


def load_ring_files():
    path = config.get('ring', 'dir')
    prefix = config.get('ring', 'prefix')
    # Read show_excluded parameter
    if config.get('ring', 'show_excluded') == 'yes':
        show_excluded = True
    else:
        show_excluded = False

    ring.clear()

    try:
        ring.load(path, prefix, show_excluded)
    except FileNotFoundError:
        print_error('Не найден ring-каталог: {}'.format(path), True)


def create_new_archive(file_name):
    global config
    global ring
    global console

    console.print_title('ARCHIVE MODE', '~', 55)

    prefix = config.get('ring', 'prefix')
    deflated = False
    if config.get('archive', 'deflated') == 'yes':
        deflated = True

    # CREATE OBJ DICT FOR ARCHIVE
    # Get dirs dict
    try:
        take_dirs_dict = config.get_section_dict('take_dirs')
    except KeyError:
        print_error('Не указана хотя бы одна папка для архивирования ' +
                    '(параметры в секции [take_dirs])', True)
    zip_dict = {}
    for dir in take_dirs_dict:
        # Folder and objects inside zip
        folder = take_dirs_dict[dir]
        # adding '/**' to end path
        if folder[-1] != '/':
            folder += '/'
        folder += '**'

        if '/*/**' in folder or '/**/**' in folder \
                or '?' in folder:
            print_error('Нельзя указывать маски файлов в пути take_dirs!\n' +
                        'указано в ' + dir + ':' + take_dirs_dict[dir],
                        True)

        recursive_objects = sorted(glob.glob(folder, recursive = True))
        zip_dict[folder] = recursive_objects


    # String - format string
    date_format = config.get('archive', 'date_format')
    date_format = date_format.replace('YYYY', '{YYYY}')
    date_format = date_format.replace('MM', '{MM}')
    date_format = date_format.replace('DD', '{DD}')
    date_format = date_format.replace('WW', '{WW}')
    date_format = date_format.replace('hh', '{hh}')
    date_format = date_format.replace('mm', '{mm}')
    date_format = date_format.replace('ss', '{ss}')

    # Take now date, take date properties
    date_now = datetime.datetime.now()
    YYYY = '{:04d}'.format(date_now.year)
    MM = '{:02d}'.format(date_now.month)
    DD = '{:02d}'.format(date_now.day)
    WW = date_now.isoweekday()
    hh = '{:02d}'.format(date_now.hour)
    mm = '{:02d}'.format(date_now.minute)
    ss = '{:02d}'.format(date_now.second)

    # Create file name
    file_name = f'{prefix}'
    file_name += date_format.format(YYYY = YYYY, MM = MM, DD = DD, WW = WW,
                                    hh = hh, mm = mm, ss = ss)
    file_name += '.zip'
    if file_name == '.zip':
        file_name = 'ring_file.zip'

    try:
        ring.new_archive(file_name, zip_dict, deflated)
    except NotADirectoryError:
        print_error('Среди списка папок [take-dirs] найден элемент, ' +
                    'не относящийся к папке!', True)

    load_ring_files()
    sort_ring_files()

def print_help():
    print('--help\t\t\t- выдает это сообщение помощи по командам')
    print('--settings -s\t\t- вывод текущих настроек программы')
    print('--test -t\t\t- ???')


def cut_mode():
    global ring
    global console
    ok = True

    message = 'CUT MODE'
    console.print_title(message, '~', 55)

    cut_type = config.get('ring', 'type')
    if cut_type == 'count':
        try:
            count = int(config.get('ring', 'count'))
            ring.cut_by_count(count)
        except:
            print_error('Неверная настройка [ring] count в файле config.')
    elif cut_type == 'age':
        try:
            max_age = int(config.get('ring', 'age'))
            ring.cut_by_age(max_age)
        except:
            print_error('Неверная настройка [ring] age в файле config.')
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
    ring_dir = config.get('ring', 'dir')
    if ring_dir[-1] != '/':
        ring_dir = ring_dir + '/'
        config.set('ring', 'dir', ring_dir)

    # Фиксим "показывать последние ... файлов": число должно быть положительным
    show_last = int(config.get('show', 'show_last'))
    if show_last < 0:
        show_last = 10
        config.set('show', 'show_last', show_last)

    # делаем нижний регистр принудительно
    config.set('ring', 'show_excluded',
               config.get('ring', 'show_excluded').lower())


def export_config():
    global config
    full_path = '{}config_exp'.format(APP_DIR)
    config.write_file(full_path)


def main():
    global console
    global CONFIG_FILE
    # Read args command line
    args = console.get_args()


    if '--version' in args:
        message = ['Version', 'Ring v.{}'.format(VERSION)]
        console.print_title(message, '*', 55)
        sys.exit()

    if '--help' in args:
        print_help()
        sys.exit()

    # Set default settings in global config
    set_config_defaults()

    # Print message and print all settings in global config
    message = ['Algorithm Computers', 'dev@a-computers.ru',
                '', '"Ring"', 'Утилита управления архивными файлами']
    console.print_title(message, '*', 55, False, False)

    if '--config' in args:
        index = args.index('--config')
        next_index = index + 1
        CONFIG_FILE = '{}{}'.format(
            get_script_dir(), args[next_index])
        try:
            test_file = open(CONFIG_FILE, 'r')
            test_file.close()
        except FileNotFoundError:
            print_error(
                "Не найден файл, указанный в параметре --config: {}".format(
                    CONFIG_FILE), True)

    if '--config-export' in args:
        export_config()

    # Read config file
    config.read_file(CONFIG_FILE)

    fix_config()

    # Load ring files (objects)
    load_ring_files()
    # Sort ring files (list)
    sort_ring_files()

    if '--settings' in args or '-s' in args:
        print('Текущие настройки программы:')
        print_settings()
        print()
        sys.exit()
    if '--cut-bad' in args:
        cut_bad_mode()
    if '--info' in args:
        pass
    if '--content' in args or '-c' in args:
        show_content_zip_file()
        sys.exit()
    if '--test' in args or '-t' in args:
        test_zip_file()
        sys.exit()

    if 'work' in args:
        pass
    if 'archive' in args:
        create_new_archive('test_file.zip')
    if 'cut' in args:
        cut_mode()
    if 'show' in args:
        show_mode()


main()
