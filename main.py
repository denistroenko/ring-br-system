from classes import *
from baseapplib import *
import glob
import socket
import sh

# GLOBAL
VERSION = '0.0.1'

console = Console()
config = Config()
ring = Ring()
letter = HtmlLetter()
email_sender = EmailSender()

APP_DIR = get_script_dir()

CONFIG_FILE = '{}config'.format(APP_DIR)


def set_config_defaults():
    global config

    # Запуск был выполнен с параметром 'period'
    config.set('run', 'period', 'no')

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

    config.set('report', 'send_to_admin', 'no')
    config.set('report', 'admin_email', '')
    config.set('report', 'send_to_user', 'no')
    config.set('report', 'user_email', '')
    config.set('report', 'logging', 'no')
    config.set('report', 'log-file', 'ring.log')

    config.set('smtp_server', 'hostname', '')
    config.set('smtp_server', 'port', '465')
    config.set('smtp_server', 'use_ssl', 'yes')
    config.set('smtp_server', 'login', '')
    config.set('smtp_server', 'password', '')
    config.set('smtp_server', 'from_address', '')

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
    config.set('remote_source', 'net_path', '')
    config.set('remote_source', 'user', '')
    config.set('remote_source', 'password', '')
    config.set('remote_source', 'smb_version', '2.0')

    # Тип remote-подключения к ring (ftp/smb/none)
    config.set('remote_ring', 'type', 'none')
    config.set('remote_ring', 'net_path', '')
    config.set('remote_ring', 'user', '')
    config.set('remote_ring', 'password', '')
    config.set('remote_ring', 'smb_version', '2.0')


    config.set('source', 'dir', '')  # Критический
    # Удаленные объекты (брать по маске). Беруться все элементы {source-files}
    # config.set('source-files', 'files', '*')  # Критический по усл.
    # Режим получения файлов для архивирования (copy/move/none)
    config.set('source', 'mode', 'copy')  # Критический по условию
    # Брать только сегодняшние файлы
    config.set('source', 'only_today_files', 'no')
    # config.set('source-dirs', '', '')  # Критический по условию
    config.set('archive', 'exclude_file_names', '')
    config.set('archive', 'deflated', 'yes')
    config.set('archive', 'compression_level', '9')
    config.set('archive', 'date_format', 'YYYY-MM-DD_WW_hh:mm:ss')


def print_settings():
    global config
    print(config)


def configure_sender():
    global config
    global email_sender

    host = config.get('smtp_server', 'hostname')
    port = int(config.get('smtp_server', 'port'))
    login = config.get('smtp_server', 'login')
    password = config.get('smtp_server', 'password')
    from_addr = config.get('smtp_server', 'from_address')
    use_ssl = False
    if config.get('smtp_server', 'use_ssl') == 'yes':
        use_ssl = True

    email_sender.configure(host, login, password, from_addr,
                               use_ssl, port)


def configure_letter_head():
    global VERSION
    global letter
    uname = os.uname()
    hostname = socket.gethostname()

    letter.append('System', 'h3', color = 'gray')
    letter.append(str(uname), color='gray')
    letter.append('hostname: ' + hostname, color='gray')
    letter.append()
    letter.append('Ring tool', 'h3', color = 'gray')
    letter.append('Version: ' + VERSION, color='gray')
    letter.append('Folder: ' + APP_DIR, color = 'gray')
    letter.append('Config file: ' + CONFIG_FILE, color='gray')
    letter.append()
    letter.append('Report', 'h3')


def print_error(error: str, stop_program: bool = False):
    global letter
    global email_sender
    global config

    send_to_admin = False
    if config.get('report', 'send_to_admin') == 'yes':
        send_to_admin = True
    admin_email = config.get('report', 'admin_email')

    if stop_program:
        print('\033[31m{}\033[37m\033[40m'.format(error))
        letter.append('Ring tool остановлена с ошибкой: ' + error,
                      color = 'red', weight = 600)
        send_emails('FATAL ERROR report from "Ring tool"')
        sys.exit()
    else:
        letter.append()
        letter.append('В Ring tool произошла ошибка: ' + error,
                      color = 'orange', weight = 600)
        print('\033[33m{}\033[37m\033[40m'.format(error))


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
    global letter
    global email_sender

    letter.append('Show mode', 'h4')

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

        letter.append('{:03d}'.format(file_no), 'span')
        letter.append('{:4d}-{:2d}-{:2d}'.format(
            date.year, date.month, date.day), 'span', border = True)
        letter.append(str(date.time), 'span')
        letter.append('{:03d}d'.format(age), 'span', border = True)
        letter.append(file_name, 'span')
        letter.append(f'{human_space(size)} {ratio}', 'span')
        letter.append('<br>', 'span')

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
    letter.append(f'Всего файлов: {ring.get_total_files()}, Занято места: ' +
         f'{human_space(total_space)}')

    send_emails()


def send_emails(subject: str = ''):
    global config
    global letter

    # Флаг режим 'period'
    is_period_mode = False
    if config.get('run', 'period') == 'yes':
        is_period_mode = True

    # Флаг "Отправлять админу"
    is_send_email_to_admin = False
    # Ставим флаг "Отправлять админу", если это в настройках
    # ИЛИ если не пустая переданная "тема письма"
    if config.get('report', 'send_to_admin') == 'yes':
        is_send_email_to_admin = True
    if subject != '':
        is_send_email_to_admin = True
        is_period_mode = True  # Здесь ставим принудительно True, чтобы
                               # логика отработала тоже принудительно в
                               # части отправления письма админу (строка 347)

    # Флаг "Отправлять пользователю"
    is_send_email_to_user = False
    if config.get('report', 'send_to_user') == 'yes':
        is_send_email_to_user = True

    # Если тема не передана, т.е. == "", то заменить на стандартную
    if subject =='':
        subject = 'Normal report from "Ring tool"'

    admin_email_address = config.get('report', 'admin_email')

    if is_period_mode and is_send_email_to_admin:
        try:
            print()
            print('Отправляю письмо администратору ({})...'.format(
                admin_email_address), end = '', flush=True)
            email_sender.send_email(admin_email_address,
                                subject, letter.get_letter(), True)
            print(' Отправлено!')
        except:
            print_error('Ошибка! Проверьте ' +\
                        'секцию smtp_server в файле конфигурации.',
                        False)


def show_content_zip_file(file_index: int = -1):
    global ring

    ok, content = ring.get_content(file_index)

    if ok:
        print(content)
    else:
        print_error(content, False)


def test_zip_file(file_index: int = -1):
    global ring

    ok, test_result = ring.test_archive(file_index)

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


def create_new_archive():
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
        source_dirs_dict = config.get_section_dict('source_dirs')
    except KeyError:
        print_error('Не указана хотя бы одна папка для архивирования ' +
                    '(параметры в секции [source_dirs])', True)
    # init
    zip_dict = {}
    for dir in source_dirs_dict:
        # Folder and objects inside zip
        folder = source_dirs_dict[dir]
        # adding '/**' to end path
        if folder[-1] != '/':
            folder += '/'
        folder += '**'

        if '/*/**' in folder or '/**/**' in folder \
                or '?' in folder:
            print_error('Нельзя указывать маски файлов в пути source_dirs!\n' +
                        'указано в ' + dir + ':' + source_dirs_dict[dir],
                        True)

        recursive_objects = sorted(glob.glob(folder, recursive = True))
        # Создаем ключ словаря и значение. Значение - это то, что вернула функция glob,
        # (она вернула список), а ключ - ключ текущий словаря source_dirs_dict
        zip_dict[dir] = recursive_objects


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

    compression_level = int(config.get('archive', 'compression_level'))
    exclude_file_names =\
        config.get('archive', 'exclude_file_names').split(',')

    only_today_files = False
    if config.get('source', 'only_today_files') == 'yes':
        only_today_files = True

    try:
        ok, new_archive_info = \
            ring.new_archive(
                             file_name, zip_dict, deflated,
                             compression_level, only_today_files,
                             exclude_file_names)
        new_archive_info = new_archive_info.replace('\n', '<br>')
    except NotADirectoryError:
        print_error('Среди списка папок [source_dirs] найден элемент, ' +
                    'не относящийся к папке!', True)

    global letter
    letter.append('Arhive mode', 'h4')
    if ok:
        letter.append(new_archive_info)
    else:
        letter.append(new_archive_info, color = 'red', weight = 600)
    letter.append('Источники:')
    for key in source_dirs_dict:
        letter.append(source_dirs_dict[key])

    if new_archive_info == '':
        print_error('Архив удален, поскольку не содержал файлов.', False)

    load_ring_files()
    sort_ring_files()

    return ok


def print_help():
    print('usage: ring archive|cut|show \n[--cut-bad] [--config file] ' +
          '[--settings] [--test] [--content] [--config-export]')
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
            print_error('Неверная настройка [ring] count в файле config.', True)
    elif cut_type == 'age':
        try:
            max_age = int(config.get('ring', 'age'))
            ring.cut_by_age(max_age)
        except:
            print_error('Неверная настройка [ring] age в файле config.', True)
    elif cut_type == 'space':
        try:
            gigabytes = round(float(config.get('ring', 'space')), 2)
            ring.cut_by_space(gigabytes)
        except:
            print_error('Неверная настройка [ring] space в файле config.', True)
    else:
        print_error('Неизвестный режим работы кольца: {}.'.format(
                    cut_type), True)

    return ok


def sort_ring_files():
    global ring
    ring.sort()


def fix_config():
    # Фиксим: последний символ в пути к папке, должен быть '/'
    ring_dir = config.get('ring', 'dir')
    if ring_dir[-1] != '/':
        ring_dir = ring_dir + '/'
        config.set('ring', 'dir', ring_dir)

    # Фиксим: последний символ в пути к папке, должен быть '/'
    target_dir = config.get('source', 'dir')
    if ring_dir[-1] != '/':
        ring_dir = ring_dir + '/'
        config.set('source', 'dir', target_dir)

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


def mount_remote_source():
    global config

    type_remote_source = config.get('remote_source', 'type')

    if type_remote_source == 'smb':
        target = config.get('source', 'dir')
        path = config.get('remote_source', 'net_path')
        user = config.get('remote_source', 'user')
        password = config.get('remote_source', 'password')
        smb_version = config.get('remote_source', 'smb_version')

        print('Монтирую удаленный источник ', path, '...', sep = '')
        try:
            sh.umount(target)
        except:
            pass

        try:
            sh.mount('-t', 'cifs', path, target, '-o',
                     'username=' + user + ',password=' + password +
                     ',iocharset=utf8' + ',file_mode=0777,dir_mode=0777,' +
                     'vers=' + smb_version)
        except sh.ErrorReturnCode_32:
            print_error('Ошибка монтирования remote_source! Устройство занято!', True)
        except:
            print_error('Ошибка монтирования remote_source!', True)


def mount_remote_ring():
    global config

    type_remote_ring = config.get('remote_ring', 'type')

    if type_remote_ring == 'smb':
        target = config.get('ring', 'dir')
        path = config.get('remote_ring', 'net_path')
        user = config.get('remote_ring', 'user')
        password = config.get('remote_ring', 'password')
        smb_version = config.get('remote_ring', 'smb_version')

        print('Монтирую удаленный ring', path, '...', sep = '')
        try:
            sh.umount(target)
        except:
            pass

        try:
            sh.mount('-t', 'cifs', path, target, '-o',
                     'username=' + user + ',password=' + password +
                     ',iocharset=utf8' + ',file_mode=0777,dir_mode=0777,' +
                     'vers=' + smb_version)
        except sh.ErrorReturnCode_32:
            print_error('Ошибка монтирования remote_ring! Устройство занято!', True)
        except:
            print_error('Ошибка монтирования remote_ring!', True)


def calculate_index_from_number(number: int):
    global ring
    files_count = ring.get_total_files()

    numbers_list = []

    for n in range(files_count):
        numbers_list.append(n + 1)

    try:
        file_index = numbers_list.index(number)
    except ValueError:
        print_error('Такого номера файла нет!')
        sys.exit()

    return file_index


def kill_archive(file_index: int):
    global ring
    ring.kill(file_index)


def main():
    global console
    global CONFIG_FILE
    # Read args command line
    args = console.get_args()

    # ИСКЛЮЧАЮЩИЕ РЕЖИМЫ (И СРАЗУ ВЫХОД)
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

    # СМЕНА НАСТРОЕК
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

    # Read config file
    config.read_file(CONFIG_FILE)

    fix_config()

    configure_sender()

    configure_letter_head()

    mount_remote_source()
    mount_remote_ring()

    # Load ring files (objects)
    load_ring_files()
    # Sort ring files (list)
    sort_ring_files()

    # ФЛАГИ
    if '-s' in args:
        print('Текущие настройки программы:')
        print_settings()
        print()
    for i in '0123456789':
        if f'-{i}' in args:
            config.set('archive', 'compression_level', i)
            config.set('archive', 'deflated', 'yes')

    # ТЕХНИЧЕСКИЕ РЕЖИМЫ РАБОТЫ
    if 'cut-bad' in args:
        cut_bad_mode()
    if 'content' in args:
        file_number = 0
        curent_arg_index = args.index('content')
        next_arg_index = curent_arg_index + 1

        try:
            next_arg = args[next_arg_index]
            file_number = int(next_arg)
        except IndexError:
            pass
        except ValueError:
            pass

        if file_number != 0:
            file_index = calculate_index_from_number(file_number)
        else:
            file_index = -1

        show_content_zip_file(file_index)
        sys.exit()
    if 'test' in args:
        file_number = 0
        curent_arg_index = args.index('test')
        next_arg_index = curent_arg_index + 1

        try:
            next_arg = args[next_arg_index]
            file_number = int(next_arg)
        except IndexError:
            pass
        except ValueError:
            pass

        if file_number != 0:
            file_index = calculate_index_from_number(file_number)
        else:
            file_index = -1

        test_zip_file(file_index)
    if 'config-export' in args:
        export_config()
    if 'kill' in args:
        file_number = 0
        curent_arg_index = args.index('kill')
        next_arg_index = curent_arg_index + 1

        try:
            next_arg = args[next_arg_index]
            file_number = int(next_arg)
        except IndexError:
            pass
        except ValueError:
            pass

        if file_number != 0:
            file_index = calculate_index_from_number(file_number)
        else:
            file_index = -1

        kill_archive(file_index)

    # ОСНОВНЫЕ РЕЖИМЫ РАБОТЫ
    if 'period' in args:
        config.set('run', 'period', 'yes')

        ok = create_new_archive()

        if ok: cut_mode()

        show_mode()
        sys.exit()
    if 'archive' in args:
        create_new_archive()
    if 'cut' in args:
        cut_mode()
    if 'show' in args:
        show_mode()


main()
