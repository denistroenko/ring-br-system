import config
import default_config
import args_parser


# Global objects
config = config.Config()


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

    load_default_settings()
    load_settings_from_file()
    load_settings_from_args()


def main():
    set_config()

    if config.run.print_all_settings == 'yes':
        print(config)



    # DELETE IT
    args_parser.print_parsed_args()
    print('config file:', config.run.config_file)
    print('mode:', config.run.mode)
    print('file number:', config.run.file_number)
    print('show count:', config.show.show_last)


if __name__ == '__main__':
    main()
