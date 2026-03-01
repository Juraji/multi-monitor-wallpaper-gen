import sys
from argparse import ArgumentParser
from pathlib import Path
import logging

from app.commands import init_cmd, setup_generate_cmd_parser, generate_cmd, setup_init_cmd_parser
from app.ui.app import MMWallpaperApp

if __name__ == '__main__':
    arg_parser = ArgumentParser(description='Batch generate multi-monitor wallpapers')
    command_parsers = arg_parser.add_subparsers(dest='command')

    # Global opts (Needed by all commands)
    arg_parser.add_argument(
        '-c', '--configuration',
        type=Path,
        default='./config.yaml',
        required=False,
        help='The configuration file to use. Defaults to ./config.yaml'
    )
    arg_parser.add_argument(
        '-d', '--debug',
        action='store_true',
        default=False,
        required=False,
        help='Debug mode. Defaults to "False".'
    )

    # Init command (Monitor detection and config init)
    init_parser = command_parsers.add_parser('init', description='Detect environment and create initial configuration')
    setup_init_cmd_parser(init_parser)

    # Generate command (Generate wallpapers based on config)
    generate_parser = command_parsers.add_parser('generate', description='Generate wallpapers')
    setup_generate_cmd_parser(generate_parser)

    ui_parser = command_parsers.add_parser('ui', description='Start in UI mode (Experimental)')

    args = arg_parser.parse_args()

    # Setup logging
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s [%(name)s %(levelname)s] %(message)s'))
    logging.root.addHandler(handler)
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.root.setLevel(log_level)

    logging.getLogger('main').info("MM Wallpaper, welcome!")

    match args.command:
        case 'ui':
            app = MMWallpaperApp()
            app.run()
        case 'init':
            init_cmd(args)
        case 'generate':
            generate_cmd(args)
        case _:
            arg_parser.print_help()
            exit(1)
