"""
Default config loader module.
Use 'load_default_config(config: object)'
"""


def init_default_config(config: object):

    config_defaults = [
        # OLD. Режим period: yes|no
        ('run', 'period', 'no'),
        # Run mode: restore|content|kill|test|cut-bad|cut|archive|show|period|
        ('run', 'mode', 'none'),
        ('run', 'file_number', '0'),
        ('run', 'config_file', '../config/default'),
        ('run', 'print_all_settings', 'no'),


        # Ring (folder of buckup files) name
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
    # Удаленные объекты (брать по маске). Беруться все элементы {source-files}
    # config.set('source-files', 'files', '*')  # Критический по усл.
    # Режим получения файлов для архивирования (copy/move/none)
    config.set('source', 'mode', 'copy')  # Критический по условию
    # Брать только сегодняшние файлы
    config.set('source', 'only_today_files', 'no')
    # config.set('source-dirs', '', '')  # Критический по условию