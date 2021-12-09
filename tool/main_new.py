import args_parser

# DELETE IT
import default_config
import config
config = config.Config()


parser = args_parser.parser


def apply_settings_from_parsed_args(config):
    """
    Apply tool global settings from parsed args (command line arguments)
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
    content_file_number = getattr(parser.parse_args(), 'content_file_number',
                                  None)
    if content_file_number != None:
        config.set('run', 'mode', 'content')
        config.set('run', 'file_number', content_file_number)

    # set 'print_all_settings'
    if parser.parse_args().settings:
        config.set('run', 'print_all_settings', 'yes')

    # Set 'config_file'
    config_file = parser.parse_args().config_file
    if config_file != '':
        config.set('run', 'config_file', config_file)


def main():
    args_parser.configure_parser()

    # set defaults settings
    default_config.set_default_config(config)

    # apply settings from config file
    config_file = parser.parse_args().config_file
    if config_file != '':  # if exist argument after '--config'
        if config.read_file(config_file) == False:
            exit()

    # apply settings from parsed args
    apply_settings_from_parsed_args(config)

    # DELETE IT
    if config.run.print_all_settings == 'yes':
        print(config)
    args_parser.print_parsed_args()
    print('config file:', config.run.config_file)
    print('mode:', config.run.mode)
    print('file number:', config.run.file_number)
    print('show count:', config.show.show_last)


if __name__ == '__main__':
    main()