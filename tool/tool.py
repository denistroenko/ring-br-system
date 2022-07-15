__version__ = '0.1.0'


import sys
sys.path.append('..')
import inspect
import glob
import socket
import re
import sh
import os
import logging
from datetime import datetime
from baseapplib import get_script_dir, human_space, configure_logger
from baseapplib import EmailSender, HtmlLetter, Console
from ring.ring import Ring as Ring
import config
import default_config
import args_parser


# GLOBAL
APP_DIR = get_script_dir(False)         # path to app dir

console = Console()                     # console object
config = config.Config()                # global config
ring = Ring()                           # ring object
letter = HtmlLetter()                   # letter object
email_sender = EmailSender()            # email_sender object

logger = logging.getLogger(__name__)    # logger obj
configure_logger(logger=logger,
                 debug_file_name=f'{APP_DIR}../log/debug.log',
                 error_file_name=f'{APP_DIR}../log/error.log',
                 start_msg= '\n\n # # #   Ring запущена  # # #',
                 )


def set_config():
    parser = args_parser.parser

    def load_default_settings():
        """
        load defaults settings
        """
        default_config.fill(config)

    def load_settings_from_file():
        """
        load settings from config file
        """
        config_file = parser.parse_args().config_file
        if config_file != '':  # if exist argument after '--config'
            if config.read_file(config_file) == False:
                exit()

    def load_settings_from_args():
        """
        load settings from parsed args
        """

        # set test mode and file number if use in command line
        test_file_number = getattr(parser.parse_args(), 'test_file_number', None)
        if test_file_number != None:
            config.set('run', 'mode', 'test')
            config.set('run', 'file_number', test_file_number)

        # set show mode and count of show last files if use in command line
        show_last = getattr(parser.parse_args(), 'show_last', None)
        if show_last != None:
            config.set('run', 'mode', 'show')
            if show_last != 0:  # if exist argument after 'show' in command line
                config.set('show', 'show_last', show_last)

        # set kill mode and file number if use in command line
        kill_file_number = getattr(parser.parse_args(), 'kill_file_number', None)
        if kill_file_number != None:
            config.set('run', 'mode', 'kill')
            config.set('run', 'file_number', kill_file_number)

        # set content mode and file number if use in command line
        restore_file_number = getattr(parser.parse_args(), 'restore_file_number',
                                      None)
        if restore_file_number != None:
            config.set('run', 'mode', 'restore')
            config.set('run', 'file_number', restore_file_number)

        # set content mode and file number if use in command line
        content_file_number = getattr(parser.parse_args(), 'content_file_number',
                                      None)
        if content_file_number != None:
            config.set('run', 'mode', 'content')
            config.set('run', 'file_number', content_file_number)

        # set period mode and start file number if use in command line
        period_file_number = getattr(parser.parse_args(), 'period_file_number',
                                    None)
        if period_file_number != None:
            config.set('run', 'mode', 'period')
            config.set('run', 'file_number', period_file_number)

        # set archive mode and start file number if use in command line
        archive_file_number = getattr(parser.parse_args(), 'archive_file_number',
                                    None)
        if archive_file_number != None:
            config.set('run', 'mode', 'archive')
            config.set('run', 'file_number', archive_file_number)

        # set cut mode and start file number if use in command line
        cut_file_number = getattr(parser.parse_args(), 'cut_file_number',
                                    None)
        if cut_file_number != None:
            config.set('run', 'mode', 'cut')
            config.set('run', 'file_number', cut_file_number)

        # set cut-bad mode and start file number if use in command line
        cutbad_file_number = getattr(parser.parse_args(), 'cutbad_file_number',
                                    None)
        if cutbad_file_number != None:
            config.set('run', 'mode', 'cut-bad')
            config.set('run', 'file_number', cutbad_file_number)

        # set 'print_all_settings'
        if parser.parse_args().settings:
            config.set('run', 'print_all_settings', 'yes')

        # Set 'config_file'
        config_file = parser.parse_args().config_file
        if config_file != '':
            config.set('run', 'config_file', config_file)

        # Set 'export_config_file'
        export_config_file = parser.parse_args().export_config_file
        if export_config_file != '':
            config.set('run', 'export_config_file', export_config_file)

    load_default_settings()
    load_settings_from_file()
    load_settings_from_args()


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

    letter.append(text='Config file: {}'.format(config.run.config_file),
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
        logger.error(error)
        console.print(msg=error, color='red')
        letter.append('Ring tool остановлена с ошибкой: ' + error,
                      color = 'red', weight = 600)
        try:
            curent_log_file_name = '%s%s' % (get_script_dir(), 'curent.log')
            curent_log_file = open(curent_log_file_name)
            curent_log = curent_log_file.readlines()
            curent_log_file.close()

            for line in curent_log:
                letter.append(line)
        except FileNotFoundError:
            logger.error('Не найден файл для считывания: %s' % curent_log_file_name)
        except:
            logger.exception(Exception)
        send_emails('FATAL ERROR report from "Ring tool"')
        sys.exit()
    else:
        logger.warning(error)
        letter.append()
        letter.append('В Ring tool произошла ошибка: ' + error,
                      color = 'orange', weight = 600)
        console.print(msg=error, color='yellow')

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
    logger.debug('Запуск режима: show')
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
    logger.info('ring-папка %s' % ring_dir)

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
            logger.info('Сканирование source...')
            print('Сканирование source...')
            recursive_objects_wo_hidden = glob.glob(folder, recursive = True)
            recursive_objects_w_hidden = glob.glob(folder + '/.*', recursive = True)
            recursive_objects = sorted(recursive_objects_wo_hidden + recursive_objects_w_hidden)
            logger.info('Сканирование завершено.')
            print('Сканирование завершено.')
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
        logger.info('Создание нового архива в ring...')

        ok, new_archive_info = \
            ring.new_archive(zip_file_name=file_name,
                             source_dir_name=source_dir,
                             objects=zip_dict,
                             deflated=deflated,
                             compression_level=compression_level,
                             only_today_files=only_today_files,
                             exclude_file_names=exclude_file_names,
                             )
        logger.info('Создание архива завершено.')

        new_archive_info = new_archive_info.replace('\n', '<br>')

    except NotADirectoryError:
        print_error('Среди списка папок [source_dirs] найден элемент, ' +
                    'не относящийся к папке!', True)
    except KeyboardInterrupt:
        print_error('\nПрервано пользователем.', True)

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
    print('usage: ring -[options] [--config config_name] '
          + '[mode] [mode argument]\n'
          + '--help\t\t\t- выдает это сообщение помощи по командам'
          )


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
            logger.exception(Exception)
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
            logger.exception(Exception)
            print_error('Ошибка монтирования remote_source! ' + \
                        'Устройство занято!', True)
        except:
            logger.exception(Exception)
            print_error('Ошибка монтирования remote_source!', True)


# ПЕРЕДЕЛАТЬ: clean & pep8
def mount_remote_ring():
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
    Восстанавливает содержимое source из указанного архива
    """

    message = 'RESTORE MODE'
    console.print_title(message, '~', 55)

    files_count = ring.get_total_files()
    if files_count == 0:
        print_error('В ring-папке нет ни одного файла! Нечего восстанавливать!')
        sys.exit()

    dir_name = config.get('source', 'dir')

    try:
        # Здесь вызывается метод объекта ring
        ok, result = ring.extract_archive(file_index=file_index,
                                          dir_name=dir_name)
    except KeyboardInterrupt:  # Обработка прерывания клавиатурой
        ok = False
        print_error('\nПрервано пользователем.', True)

    if ok:
        console.print(msg=result, color='green')
    else:
        print_error(result, True)


def main():
    set_config()

    if config.run.print_all_settings == 'yes':
        print(config)



    # DELETE IT
    args_parser.print_parsed_args()
    print('config file:', config.run.config_file)
    print('export config file:', config.run.export_config_file)
    print('mode:', config.run.mode)
    print('file number:', config.run.file_number)
    print('show count:', config.show.show_last)



    ok = default_config.fix_config(config, print_error)
    if ok == False:
        sys.exit()

    configure_sender()
    configure_letter_head()

    # Load ring files (objects)
    load_ring_files()
    # Sort ring files (list)
    sort_ring_files()

    # ТЕХНИЧЕСКИЕ РЕЖИМЫ РАБОТЫ
    if config.run.mode == 'cut-bad':
        cut_bad_mode()

    if config.run.mode == 'content':
        file_number = config.run.filenumber

        if file_number != 0:
            file_index = calculate_index_from_number(file_number)
        else:
            file_index = -1

        show_content_zip_file(file_index)
        sys.exit()

    if config.run.mode == 'test':
        file_number = config.run.file_number

        if file_number != 0:
            file_index = calculate_index_from_number(file_number)
        else:
            file_index = -1

        test_zip_file(file_index)
    if config.run.mode == 'config-export':
        export_config()

    if config.run.mode == 'kill':
        file_number = config.run.file_number

        if file_number != 0:
            file_index = calculate_index_from_number(file_number)
        else:
            file_index = -1

        kill_archive(file_index)

    # ОСНОВНЫЕ РЕЖИМЫ РАБОТЫ
    if config.run.mode == 'show':
        show_mode()

    if config.run.mode == 'cut':
        cut_mode()

    mount_remote_source()

    if config.run.mode == 'restore':
        file_number = config.run.file_number

        if file_number != 0:
            file_index = calculate_index_from_number(file_number)
        else:
            file_index = -1

        restore_source(file_index)

    if config.run.mode == 'period':
        config.set('run', 'period', 'yes')
        ok = create_new_archive()
        if ok:
            cut_mode()
        show_mode()
        sys.exit()

    if config.run.mode == 'archive':
        create_new_archive()


if __name__ == '__main__':
    main()
