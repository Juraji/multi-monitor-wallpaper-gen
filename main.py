import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

from app.commands import GenerateCommand
from app.commands.init_cmd import InitCommand

if __name__ == '__main__':
    arg_parser = ArgumentParser(description='Batch generate multi-monitor wallpapers')

    # Global opts (Needed by all commands)
    arg_parser.add_argument(
        '-c', '--configuration',
        type=Path,
        default='./profiles/default.yaml',
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

    command_parser = arg_parser.add_subparsers(dest='command')

    # Init command (Monitor detection and config init)
    init_parser = InitCommand(command_parser)

    # Generate command (Generate wallpapers based on config)
    generate_cmd = GenerateCommand(command_parser)

    # Parse arguments
    args = arg_parser.parse_args()

    # Setup logging
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s [%(name)s %(levelname)s] %(message)s'))
    logging.root.addHandler(handler)
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.root.setLevel(log_level)

    logging.getLogger('main').info("MM Wallpaper, welcome!")

    match args.command:
        case init_parser.command:
            init_parser.execute(args)
        case generate_cmd.command:
            generate_cmd.execute(args)
        case _:
            arg_parser.print_help()
            exit(1)
