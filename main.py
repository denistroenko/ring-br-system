__version__ = '0.0.3'

import glob
import socket
import re
import sh
import os
import sys

from datetime import datetime
from baseapplib import get_script_dir, human_space
from baseapplib import EmailSender, HtmlLetter, Config, Console
from classes import Ring, RingFile


# GLOBAL

APP_DIR = get_script_dir()                # path to app dir
CONFIG_FILE = '{}config'.format(APP_DIR)  # path to config file

console = Console()             # console object
args = console.get_args()       # argumetns from console
config = Config()               # global config
ring = Ring()                   # ring object
letter = HtmlLetter()           # letter object
email_sender = EmailSender()    # email_sender object


# ПЕРЕДЕЛАТЬ: clean & pep8
def set_config_defaults():
    global config

    # Запуск был выполнен с параметром 'period'

    config_defaults = [
        ('run', 'period', 'no'),

        ('ring', 'name', 'noname'),
        ('ring', 'dir', '/mnt/ring/'),
        ('ring', 'prefix', ''),
        ('ring', 'count', '30'),
        ('ring', 'age', '180'),
        ('ring', 'space', '200'),
        ('ring', 'type', 'count'),
        ('ring', 'show_excluded', 'no'),

        ('report', 'send_to_admin', 'no'),
        ('report', 'create_bitrix24_task', 'no'),
        ('report', 'admin_email', ''),
        ('report', 'send_to_user', 'no'),
        ('report', 'user_email', ''),
        ('report', 'logging', 'no'),
        ('report', 'log-file', 'ring.log'),

        ('bitrix24', 'web_hook', ''),

        ('smtp_server', 'hostname', ''),
        ('smtp_server', 'port', '465'),
        ('smtp_server', 'use_ssl', 'yes'),
        ('smtp_server', 'login', ''),
        ('smtp_server', 'password', ''),
        ('smtp_server', 'from_address', ''),

        ('show', 'show_last', '15'),
        ('show', 'green_min', '-5'),
        ('show', 'green_max', '5'),
        ('show', 'red_min', '-20'),
        ('show', 'red_max', '20'),
        ('show', 'green_age', '7'),

        ('remote_source', 'type', 'none'),
        ('remote_source', 'net_path', ''),
        ('remote_source', 'user', ''),
        ('remote_source', 'password', ''),
        ('remote_source', 'smb_version', '2.0'),

        ('remote_ring', 'type', 'none'),
        ('remote_ring', 'net_path', ''),
        ('remote_ring', 'user', ''),
        ('remote_ring', 'password', ''),
        ('remote_ring', 'smb_version', '2.0'),

        ('archive', 'exclude_file_names', ''),
        ('archive', 'deflated', 'yes'),
        ('archive', 'compression_level', '9'),
        ('archive', 'date_format', 'YYYY-MM-DD_WW_hh:mm:ss'),
    ]

    for section, parameter, value in config_defaults:
        config.set(section, parameter, value)


    config.set('source', 'dir', '')  # Критический
    # Удаленные объекты (брать по маске). Беруться все элементы {source-files}
    # config.set('source-files', 'files', '*')  # Критический по усл.
    # Режим получения файлов для архивирования (copy/move/none)
    config.set('source', 'mode', 'copy')  # Критический по условию
    # Брать только сегодняшние файлы
    config.set('source', 'only_today_files', 'no')
    # config.set('source-dirs', '', '')  # Критический по условию


def print_settings():
    """
    Вывод на экран __str__ объекта config,
    т.е. всей глобальной конфигурации
    """
    print(config)


def configure_sender():
    """
    Эта функция начально конфигурирует объект email_sender
    из настроек глобальной конфигурации
    """
    host = config.get('smtp_server', 'hostname')
    port = int(config.get('smtp_server', 'port'))
    login = config.get('smtp_server', 'login')
    password = config.get('smtp_server', 'password')
    from_addr = config.get('smtp_server', 'from_address')

    use_ssl = False
    if config.get('smtp_server', 'use_ssl') == 'yes':
        use_ssl = True

    email_sender.configure(smtp_hostname=host,
                           login=login,
                           password=password,
                           from_address=from_addr,
                           use_ssl=use_ssl,
                           port=port,
                           )


def configure_letter_head():
    """
    Изначальное заполнение шапки письма (объект letter). Добавляются в шапку
    стандартные данные о системе, версии ring и имени файла конфигурации
    """
    uname = os.uname()
    hostname = socket.gethostname()

    letter.append(text='System',
                  tag_type='h3',
                  color='gray',
                  )

    letter.append(text=str(uname).replace('#', ''),
                  color = 'gray',
                  )

    letter.append(text='hostname: {}'.format(hostname),
                  color = 'gray',
                  )

    letter.append()

    letter.append(text='Ring tool',
                  tag_type='h3',
                  color = 'gray',
                  )

    letter.append(text='Version: {}'.format(__version__),
                  color = 'gray',
                  )

    letter.append(text='Folder: {}'.format(APP_DIR),
                  color = 'gray',
                  )

    letter.append(text='Config file: {}'.format(CONFIG_FILE),
                  color = 'gray',
                  )

    letter.append()

    letter.append(text='Report',
                  tag_type='h3',
                  )


# ПЕРЕДЕЛАТЬ: clean & pep8
def print_error(error: str, stop_program: bool = False):
    global letter
    global email_sender
    global config

    ok = True
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

    return ok


# ПЕРЕДЕЛАТЬ:   clean & pep8
def print_file_line(number,
                    year, month, day, time, age, file_name, file_size,
                    difference, show_plus_space: bool,
                    color_date = '\033[30m\033[47m',
                    color_time = '\033[37m\033[40m',
                    color_age = '\033[30m\033[47m',
                    color_file_name = '\033[37m\033[40m',
                    color_file_size = '\033[537m\033[40m',
                    color_difference = '\033[32m\033[40m',
                    color_default = '\033[37m\033[40m',
                    date_separator = '-',
                    ):

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


# ПЕРЕДЕЛАТЬ: clean & pep8
def show_mode():
    ok = True

    letter.append('Show mode', 'h4')

    if int(config.get('show', 'show_last')) > 0:
        short = True
    else:
        short = False

    ring_type = config.get('ring', 'type')
    if ring_type == 'count':
        ring_type_value = config.get('ring', 'count')
    elif ring_type == 'age':
        ring_type_value = config.get('ring', 'age')
    else:
        ring_type_value = config.get('ring', 'space')

    ring_name = config.get('ring', 'name')

    message = ['SHOW RING MODE']
    message.append('type: ' + ring_type + ' (' + ring_type_value + ')')
    message.append('')
    if ring_name != 'noname':
        message.append('>>> {} <<<'.format(ring_name))

    console.print_title(message, '~', 55)

    ring_dir = config.get('ring', 'dir')
    print(ring_dir)

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
            pass # color_difference = color_difference
        elif ratio >= red_min and ratio <= red_max:
            color_difference = '\033[31m'
        else:
            color_difference = '\033[37m\033[41m'

        print_file_line(number=file_no,
                        year=date.year,
                        month=date.month,
                        day=date.day,
                        time=time,
                        age=age,
                        file_name=file_name,
                        file_size=size,
                        difference=ratio,
                        show_plus_space=show_plus_space,
                        color_difference=color_difference,
                        color_age=color_age,
                        color_date=color_date,
                        )
        prev_size = size
        total_space = ring.get_total_space()


    print('~' * 55)

    if ring_type == 'space':
        msg_inside_bar = ('Всего файлов: {}'.format(ring.get_total_files())
                           + '; Занято места: {} из {}G'.format(
                                   human_space(total_space),
                                   ring_type_value,
                                   )
                          )

        percents = total_space / (int(ring_type_value) * 1024**3) * 100
        console.print_progress_bar(percents=percents,
                                   width=55,
                                   fill_symbol=' ',
                                   used_bg_color='purple',
                                   avaiable_bg_color='blue',
                                   msg=msg_inside_bar,
                                   )
    elif ring_type == 'count':
        msg_inside_bar = ('Всего файлов: {} из {}'.format(
                                  ring.get_total_files(),
                                  ring_type_value,
                                  )
                          + '; Занято места: {}'.format(
                                  human_space(total_space),
                                  )
                          )
        percents = ring.get_total_files() / int(ring_type_value) * 100
        console.print_progress_bar(percents=percents,
                                   width=55,
                                   fill_symbol=' ',
                                   used_bg_color='purple',
                                   avaiable_bg_color='blue',
                                   msg=msg_inside_bar,
                                   )
    else:
        msg_inside_bar = ('Всего файлов: {}'.format(ring.get_total_files())
                          + '; Занято места: {}'.format(
                                  human_space(total_space),
                                  )
                          )
        print(msg_inside_bar)

    print()

    letter.append(f'Всего файлов: {ring.get_total_files()}, Занято места: ' +
         f'{human_space(total_space)}')

    send_emails()
    sys.exit()


# ПЕРЕДЕЛАТЬ: clean & pep8
def send_emails(subject: str = ''):
    global config
    global letter
    global console

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
        # Отправляем в Битрикс24
        if config.get('report', 'create_bitrix24_task').lower() == 'yes':
            def cleanhtml(raw_html):
                # cleanr = re.compile('<.*?>')
                cleanr = re.compile('<.*?>')
                cleantext = re.sub(cleanr, '', raw_html)
                return cleantext

            WEB_HOOK = config.get('bitrix24', 'web_hook')
            descriprion_bx24 = letter.get_letter()
            descriprion_bx24 = cleanhtml(descriprion_bx24)
            try:
                from bitrix24 import Bitrix24
                from bitrix24 import BitrixError
                print()
                console.print(
                    'Ставлю задачу администратору в Битрикс24...',
                    end =' ',
                    effect = '6',
                    flush = True,
                )
                bx24 = Bitrix24(WEB_HOOK)
                bx24.callMethod('tasks.task.add',
                                fields={'TITLE': subject, 'RESPONSIBLE_ID': 1,
                                        'DESCRIPTION': descriprion_bx24})
                console.print(
                    'ok',
                    color = 'green'
                )
            except Exception as message:
                print_error(
                    'Ошибка при работе с Битрикс24: {}.'.format(message),
                    False,
                )
                letter.append('')
                letter.append('Ошибка постановки задачи в Битрикс24!',
                              weight = 600, color = 'red')
        # Отправляем email
        try:
            print()
            console.print(
                'Отправляю письмо администратору ({})...'.format(
                admin_email_address),
                end = ' ',
                flush=True,
            )
            email_sender.send_email(admin_email_address,
                                subject, letter.get_letter(), True)
            console.print('ok', color = 'green')
        except:
            print_error('Ошибка! Проверьте ' +\
                        'секцию smtp_server в файле конфигурации.',
                        False)
        # END TEST


# ПЕРЕДЕЛАТЬ: clean & pep8
def show_content_zip_file(file_index: int = -1):
    """
    Выводит на экран содержимое zip-архива.
    Один из основных режимов работы программы.
    """
    # Определяем номер файла по индексу (строковая переменная).
    # Если индекс = -1, то номер представить как "last"
    file_number = str(file_index + 1)
    if file_index == -1:
        file_number = 'last'

    message = ['CONTENT SHOW MODE', 'file number: {}'.format(file_number)]
    console.print_title(title=message, border_symbol='~', width=55)

    # Получаем переменные УСПЕХ и КОНТЕНТ
    ok, content = ring.get_content(file_index)

    if ok:
        print(content)
    else:
        print_error(content, False)


def test_zip_file(file_index: int=-1):
    """
    Функция тестирует архив в ring-директории, но фактически -
    делает это через метод объекта ring
    """
    ok, test_result = ring.test_archive(file_index)

    if ok:
        print(test_result)
    else:
        print_error(test_result, stop_program=False)


# ПЕРЕДЕЛАТЬ: clean & pep8
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
    """
    Функция "загружает" объект ring файлами,
    по сути - вызов метода ring.load()
    """
    path = config.get('ring', 'dir')
    prefix = config.get('ring', 'prefix')

    show_excluded = False
    if config.get('ring', 'show_excluded') == 'yes':
        show_excluded = True

    # Очистка ring
    ring.clear()

    try:
        ring.load(path, prefix, show_excluded)
    except FileNotFoundError:
        print_error('Не найден ring-каталог: {}'.format(path),
                    stop_program=True,
                    )


# ПЕРЕДЕЛАТЬ: clean & pep8
def create_new_archive():
    console.print_title('ARCHIVE MODE', '~', 55)

    source_dir = config.get('source', 'dir')
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
        if folder[:2] == './':
            folder = source_dir + folder[2:]
        # adding '/**' to end path
        if folder[-1] != '/':
            folder += '/'
        folder += '**'

        if '/*/**' in folder or '/**/**' in folder \
                or '?' in folder:
            print_error('Нельзя указывать маски файлов в пути source_dirs!\n' +
                        'указано в ' + dir + ':' + source_dirs_dict[dir],
                        True)

        console.print(
            'Сканирую {} ({})... '.format (dir, folder[:-2]),
            end = '',
            effect = '6',
            flush = True,
        )
        try:
            recursive_objects = sorted(glob.glob(folder, recursive = True))
        except KeyboardInterrupt:
            console.print(msg='\nПрервано пользователем.',
                          color='yellow')
            sys.exit()

        console.print('ok', color = 'green')
        # Создаем ключ словаря и значение. Значение - это то,
        # что вернула функция glob (она вернула список),
        # а ключ - ключ текущий словаря source_dirs_dict
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
    date_now = datetime.now()
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
            ring.new_archive(zip_file_name=file_name,
                             source_dir_name=source_dir,
                             objects=zip_dict,
                             deflated=deflated,
                             compression_level=compression_level,
                             only_today_files=only_today_files,
                             exclude_file_names=exclude_file_names,
                             )
        new_archive_info = new_archive_info.replace('\n', '<br>')
    except NotADirectoryError:
        print_error('Среди списка папок [source_dirs] найден элемент, ' +
                    'не относящийся к папке!', True)

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


# ПЕРЕДЕЛАТЬ: clean & pep8
def print_help():
    print('usage: ring archive|cut|show \n[--cut-bad] [--config file] ' +
          '[--settings] [--test] [--content] [--config-export]')
    print('--help\t\t\t- выдает это сообщение помощи по командам')
    print('--settings -s\t\t- вывод текущих настроек программы')
    print('--test -t\t\t- ???')


# ПЕРЕДЕЛАТЬ: clean & pep8
def cut_mode():
    ok = True

    message = 'CUT MODE'
    console.print_title(message, '~', 55)

    cut_type = config.get('ring', 'type')
    if cut_type == 'count':
        try:
            count = int(config.get('ring', 'count'))
            ring.cut_by_count(count)
        except:
            print_error('Неверная настройка [ring] count в файле config.',
                        True)
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
            print_error('Неверная настройка [ring] space в файле config.',
                        True)
    else:
        print_error('Неизвестный режим работы кольца: {}.'.format(
                    cut_type), True)

    return ok


def sort_ring_files():
    """
    Сортировка ring
    """
    ring.sort()


# ПЕРЕДЕЛАТЬ: clean & pep8
def fix_config():
    # Фиксим: последний символ в пути к папке, должен быть '/'
    ring_dir = config.get('ring', 'dir')
    if ring_dir[-1] != '/' and ring_dir != '':
        ring_dir = ring_dir + '/'
        config.set('ring', 'dir', ring_dir)

    # Фиксим: последний символ в пути к папке, должен быть '/'
    source_dir = config.get('source', 'dir')
    if source_dir != '':
        if source_dir[-1] != '/':
            source_dir = source_dir + '/'
            config.set('source', 'dir', source_dir)

    # Фиксим "показывать последние ... файлов": число должно быть положительным
    show_last = int(config.get('show', 'show_last'))
    if show_last < 0:
        show_last = 10
        config.set('show', 'show_last', show_last)

    # делаем нижний регистр принудительно
    config.set('ring', 'show_excluded',
               config.get('ring', 'show_excluded').lower())

    # Если есть список source_dirs, но нет параметра [source] dir
    try:
        source_dirs_dict = {}
        source_dirs_dict = config.get_section_dict('source_dirs')
        source_dir = config.get('source', 'dir')
        if source_dirs_dict != {} and \
                source_dir == '':
            msg = ('Указан список source_dirs, но не указан параметр dir ' +
                   'в секции source. Это может привести к неверным именам ' +
                   'внутри архива. Продолжение работы невозможно!')
            print_error(msg, True)
    except:
        # except может быть, если нет параметров в секции source_dirs
        pass


def export_config():
    """
    Экспорт конфигурации в файл ./config_ext,
    по сути - вызвывает метод объекта config
    """
    full_path = '{}config_exp'.format(APP_DIR)
    config.write_file(full_path)


# ПЕРЕДЕЛАТЬ: clean & pep8
def mount_remote_source():
    global config
    global console

    type_remote_source = config.get('remote_source', 'type')

    if type_remote_source == 'smb':
        target = config.get('source', 'dir')
        path = config.get('remote_source', 'net_path')
        user = config.get('remote_source', 'user')
        password = config.get('remote_source', 'password')
        smb_version = config.get('remote_source', 'smb_version')

        console.print(
            'Демонтирую удаленный источник {}... '.format(path),
            end = '',
            effect = '6',
            flush = True,
        )
        try:
            sh.umount(target)
            console.print('ok', color = 'green')
        except:
            console.print('ok', color = 'green')

        console.print(
            'Монтирую удаленный источник {}... '.format(path),
            end = '',
            effect = '6',
            flush = True,
        )
        try:
            sh.mount('-t', 'cifs', path, target, '-o',
                     'username=' + user + ',password=' + password +
                     ',iocharset=utf8' + ',file_mode=0777,dir_mode=0777,' +
                     'vers=' + smb_version)
            console.print('ok', color = 'green')
        except sh.ErrorReturnCode_32:
            print_error('Ошибка монтирования remote_source! ' + \
                        'Устройство занято!', True)
        except:
            print_error('Ошибка монтирования remote_source!', True)


# ПЕРЕДЕЛАТЬ: clean & pep8
def mount_remote_ring():
    global config
    global console

    type_remote_ring = config.get('remote_ring', 'type')

    if type_remote_ring == 'smb':
        target = config.get('ring', 'dir')
        path = config.get('remote_ring', 'net_path')
        user = config.get('remote_ring', 'user')
        password = config.get('remote_ring', 'password')
        smb_version = config.get('remote_ring', 'smb_version')

        console.print(
            'Демонтирую удаленный ring {}... '.format(path),
            end = '',
            effect = '6',
            flush = True,
        )
        try:
            sh.umount(target)
            console.print('ok', color = 'green')
        except:
            console.print('ok', color = 'green')

        console.print(
            'Монтирую удаленный ring {}... '.format(path),
            flush = True,
            effect = '6',
            end = '',
        )
        try:
            sh.mount('-t', 'cifs', path, target, '-o',
                     'username=' + user + ',password=' + password +
                     ',iocharset=utf8' + ',file_mode=0777,dir_mode=0777,' +
                     'vers=' + smb_version)
            console.print('ok', color = 'green')
        except sh.ErrorReturnCode_32:
            print_error('Ошибка монтирования remote_ring!' + \
                        ' Устройство занято!', True)
        except:
            print_error('Ошибка монтирования remote_ring!', True)


def calculate_index_from_number(number: int) -> int:
    """
    Вычисляет номер файла исходя из его индекса путем формирования
    СПИСКА, содержащего числа (эквиваленты номеров файлов в ring).
    Похоже, что сложности это только для того, чтобы именно здесь определить,
    есть ли такой номер файла в ring, не обращаясь в сам ring,
    и исключение отловить здесь, и не связанное с объектом rung
    """
    # Определяем количество файлов в ring-папке
    files_count = ring.get_total_files()

    # Создаем пустой список номеров файлов
    numbers_list = []

    # Заполняем список номерами
    for n in range(files_count):
        numbers_list.append(n + 1)

    # Проверяем на исключение
    try:
        # Запрашиваем индекс нужного номера в списке номеров
        file_index = numbers_list.index(number)
    except ValueError:
        print_error('Такого номера файла нет!')
        sys.exit()

    return file_index


def kill_archive(file_index: int):
    """
    Функция удаляет архив из ring-папки, но по сути -
    вызывает метод объекта ring
    """
    files_count = ring.get_total_files()
    if files_count == 0:
        print_error('В ring-папке нет ни одного файла! Нечего удалять!')
        sys.exit()

    ring.kill(file_index)


def restore_source(file_index: int):
    """
    Восстанавливает соержимое source, УДАЛЯЯ перед этим все файлы из source
    """

    message = 'RESTORE MODE'
    console.print_title(message, '~', 55)

    # НАПИСАТЬ УДАЛЕНИЕ ВСЕХ ФАЙЛОВ !!!

    files_count = ring.get_total_files()
    if files_count == 0:
        print_error('В ring-папке нет ни одного файла! Нечего восстанавливать!')
        sys.exit()

    dir_name = config.get('source', 'dir')
    ok, result = ring.extract_archive(dir_name=dir_name)

    if ok:
        pass
    else:
        print_error(result, True)



def apply_alternative_config_file():
    global CONFIG_FILE

    try:
        index = args.index('--config')
    except ValueError:
        index = args.index('-c')

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


# ПЕРЕДЕЛАТЬ: clean & pep8
def main():
    # ИСКЛЮЧАЮЩИЕ РЕЖИМЫ (И СРАЗУ ВЫХОД)
    if '--version' in args or \
            '-V' in args:
        message = ['Algorithm Computers', 'dev@a-computers.ru',
                   '', 'Ring v.{}'.format(__version__),
                   'Утилита управления архивными файлами']

        console.print_title(message, '*', 55, False, False)
        sys.exit()
    if '--help' in args:
        print_help()
        sys.exit()

    # Set default settings in global config
    set_config_defaults()

    # if use alternative config file
    if '--config' in args or \
            '-c' in args:
        apply_alternative_config_file()

    # Read config file
    config.read_file(CONFIG_FILE)

    ok = fix_config()
    if ok == False:
        sys.exit()

    configure_sender()

    configure_letter_head()

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
    if 'show' in args:
        show_mode()
    if 'cut' in args:
        cut_mode()

    mount_remote_source()

    if 'restore' in args:
        file_number = 0
        curent_arg_index = args.index('restore')
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

        restore_source(file_index)

    if 'period' in args:
        config.set('run', 'period', 'yes')
        ok = create_new_archive()
        if ok:
            cut_mode()
        show_mode()
        sys.exit()

    if 'archive' in args:
        create_new_archive()


if __name__ == '__main__':
    main()
