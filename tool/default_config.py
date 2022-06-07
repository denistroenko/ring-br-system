"""
Module content default config loader.
"""


def fill(config: object):

    config_defaults = [
        # [run] section
        ('run', 'period', 'no'),              # OLD. Режим period: yes|no
        ('run', 'mode', 'none'),              # Run mode
        ('run', 'file_number', '0'),          # Номер файла (аргумент режимов)
        ('run', 'config_file', './config/default'),    # файл конфигурации
        ('run', 'export_config_file', './config/exp_default'),  # файл экспорта конфигурации
        ('run', 'print_all_settings', 'no'),  # Флаг "Печатать все настройки"





        # Ring (folder of buckup files)
        ('ring', 'name', 'Ring archive folder'),
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

        # ('remote_ring', 'type', 'none'),
        # ('remote_ring', 'net_path', ''),
        # ('remote_ring', 'user', ''),
        # ('remote_ring', 'password', ''),
        # ('remote_ring', 'smb_version', '2.0'),

        ('archive', 'exclude_file_names', ''),
        ('archive', 'deflated', 'yes'),
        ('archive', 'compression_level', '9'),
        ('archive', 'date_format', 'YYYY-MM-DD_WW_hh:mm:ss'),
    ]

    for section, parameter, value in config_defaults:
        config.set(section, parameter, value)


    config.set('source', 'dir', '')  # Критический
    # Режим получения файлов для архивирования (copy/move/none)
    config.set('source', 'mode', 'copy')  # Критический по условию
    # Брать только сегодняшние файлы
    config.set('source', 'only_today_files', 'no')
    # config.set('source-dirs', '', '')  # Критический по условию
