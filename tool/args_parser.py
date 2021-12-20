"""
agrs_pagser module. Content parser object for ring tool.

usage:
from args_parser import parser
"""

__version__ = '0.0.0'


import sys
sys.path.append('..')
import argparse


# Global parcer object
parser = argparse.ArgumentParser()


def configure(parser: object) -> None:
    """
    This function configure parser: set all subparsers, positional
    and optional agruments, help.
    Need parser object.
    """

    # Descriotion
    parser.description = 'ring tool - part of Ring Backup&Recovery System. ' \
            + 'Command line tool.'

    # Optional argument --config,
    parser.add_argument('-c',
                        '--config',
                        type=str,
                        default='',
                        dest='config_file',
                        action='store',
                        help='config file',
                        )

    # Optional argument --settings
    parser.add_argument('-s',
                        '--settings',
                        default=False,
                        action='store_true',
                        help='show all config settings',
                        )

    # Optional argument --version
    parser.add_argument('-V',
                        '--version',
                        action='version',
                        version='version: %s' %__version__,
                        )

    # Subparsers (MODES)
    subparsers = parser.add_subparsers(help='modes')

    # Subparser 'show'
    show_parser = subparsers.add_parser('show',
                                        help='show ring of archives',
                                        )
    # Positional argument of subparser 'show'
    show_parser.add_argument('show_last',
                             nargs='?',
                             action='store',
                             type=int,
                             default=0,
                             help='count of files for show mode',
                             )

    # Subparser 'test'
    test_parser = subparsers.add_parser('test',
                                        help='test archive file',
                                        )

    # Positional argument of subparser 'test'
    test_parser.add_argument('test_file_number',
                             nargs='?',
                             action='store',
                             type=int,
                             default=0,
                             help='file number for test mode',
                             )

    # Subparser 'kill'
    kill_parser = subparsers.add_parser('kill',
                                        help='kill archive file mode',
                                        )
    # Positional argument of subparser 'kill'
    kill_parser.add_argument('kill_file_number',
                             nargs='?',
                             action='store',
                             type=int,
                             default=0,
                             help='file number for kill mode',
                             )

    # Subparser 'restore'
    content_parser = subparsers.add_parser('restore',
                                           help='restore files  mode',
                                           )
    # Positional argument of subparser 'restore'
    content_parser.add_argument('restore_file_number',
                                nargs='?',
                                action='store',
                                type=int,
                                default=0,
                                help='file number for restore mode',
                                )

    # Subparser 'content'
    content_parser = subparsers.add_parser('content',
                                           help='content show mode',
                                           )
    # Positional argument of subparser 'content'
    content_parser.add_argument('content_file_number',
                                nargs='?',
                                action='store',
                                type=int,
                                default=0,
                                help='file number for content mode',
                                )

    # Subparser 'cut-bad
    content_parser = subparsers.add_parser('cut-bad',
                                           help='cut bad backup files mode',
                                           )
    # Positional argument of subparser 'cut-bad'
    content_parser.add_argument('cutbad_file_number',
                                nargs='?',
                                action='store',
                                type=int,
                                default=0,
                                help='start file number for cut-bad mode',
                                )

def print_parsed_args():
    """
    This test function print parse_args
    """
    print(parser.parse_args())


def main():
    """
    This is main function print message about this modile.
    This module is not intended to run as an entry point
    (if __name__ = '__main__').
    """
    print('args_parser module is not intended to run as an entry point.')


if __name__ == '__main__':
    main()
else:
    configure(parser)
