__version__ = '0.0.0'


import argparse


#GLOBAL
parser = argparse.ArgumentParser()


def configure_parser():
    # parser.prefix_chars = ''
    parser.description = 'Rign remote backup&restore tool'

    parser.add_argument('-c',
                             '--config',
                             type=str,
                             default='config',
                             dest='config_file_path',
                             action='store',
                             help='config file path',
                             )


    parser.add_argument('-s',
                             '--settings',
                             default=False,
                             action='store_true',
                             help='show all config settings',
                             )

    # Subparsers (MODES)
    subparsers = parser.add_subparsers(help='modes')


    # Subparser show
    show_parser = subparsers.add_parser('show',
                                        help='show ring of archives',
                                        )
    show_parser.add_argument('show_count',
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

    test_parser.add_argument('test_number',
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

    kill_parser.add_argument('kill_number',
                             nargs='?',
                             action='store',
                             type=int,
                             default=0,
                             help='file number for kill',
                             )

    parser.add_argument('-V',
                             '--version',
                             action='version',
                             version='version: %s' %__version__,
                             )


def print_parsed_args():
    print(parser.parse_args())


def main():
    configure_parser()
    print_parsed_args()


if __name__ == '__main__':
    main()
