__version__ = '0.0.0'


import sys
sys.path.append('..')


import argparse


#GLOBAL
parser = argparse.ArgumentParser()


def configure_parser():
    parser.description = 'ring tool - part of RING Backup&Restore System. ' \
            + 'Command line tool.'

    parser.add_argument('-c',
                        '--config',
                        type=str,
                        default='',
                        dest='config_file',
                        action='store',
                        help='config file',
                        )

    parser.add_argument('-s',
                        '--settings',
                        default=False,
                        action='store_true',
                        help='show all config settings',
                        )

    parser.add_argument('-V',
                        '--version',
                        action='version',
                        version='version: %s' %__version__,
                        )

    # Subparsers (MODES)
    subparsers = parser.add_subparsers(help='modes')

    # Subparser show
    show_parser = subparsers.add_parser('show',
                                        help='show ring of archives',
                                        )
    show_parser.add_argument('show_last',
                             nargs='?',
                             action='store',
                             type=int,
                             default=0,
                             help='count of files for show',
                             )

    # Subparser test
    test_parser = subparsers.add_parser('test',
                                        help='test archive file',
                                        )

    test_parser.add_argument('test_file_number',
                             nargs='?',
                             action='store',
                             type=int,
                             default=0,
                             help='file number for test',
                             )

    # Subparser kill
    kill_parser = subparsers.add_parser('kill',
                                        help='kill archive file',
                                        )

    kill_parser.add_argument('kill_file_number',
                             nargs='?',
                             action='store',
                             type=int,
                             default=0,
                             help='file number for kill',
                             )

    # Subparser content
    content_parser = subparsers.add_parser('content',
                                           help='content show mode',
                                           )

    content_parser.add_argument('content_file_number',
                                nargs='?',
                                action='store',
                                type=int,
                                default=0,
                                help='file number for content',
                                )


def print_parsed_args():
    print(parser.parse_args())


def main():
    print('This is args_parser.')


if __name__ == '__main__':
    main()
