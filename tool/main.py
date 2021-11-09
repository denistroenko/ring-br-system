import sys
sys.path.append("..") # Adds higher directory to python modules path.
import core
from args_parser import parser


def apply_settings_from_parsed_args():
    """
    Применяет глобальные настройки ядра исходя из распарсеных аргументов
    командной строки
    """

    # Проверить и применить режим test
    try:
        test_number = parser.parse_args().test_number
    except:
        pass
    else:
       core.settings.MODE = 'test'
       core.settings.FILE_NUMBER = test_number

    # Проверить и применить режим show
    try:
        show_count = parser.parse_args().show_count
    except:
        pass
    else:
       core.settings.MODE = 'show'

    # Проверить и применить режим kill
    try:
        kill_number = parser.parse_args().kill_number
    except:
        pass
    else:
       core.settings.MODE = 'kill'
       core.settings.FILE_NUMBER = kill_number


def main():
    # args_parser.configure_parser()
    # args_parser.print_parsed_args()
    # apply_settings_from_parsed_args()
    # print('Mode:', core.settings.MODE)
    # print('file number', core.settings.FILE_NUMBER)

    core.ring.config.set('ring', 'name' , '!!!!!!!!!!')
    core.ring.main()


if __name__ == '__main__':
    main()
