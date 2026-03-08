import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

from app.commands import GenerateCommand, Command, InitCommand

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

    command_arg_parser = arg_parser.add_subparsers(dest='command')
    commands: list[Command] = [
        InitCommand(command_arg_parser),
        GenerateCommand(command_arg_parser),
    ]

    # Parse arguments
    args = arg_parser.parse_args()

    # Setup logging
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s [%(name)s %(levelname)s] %(message)s'))
    logging.root.addHandler(handler)
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.root.setLevel(log_level)

    logging.getLogger('main').info("MM Wallpaper, welcome!")

    for command in commands:
        if args.command == command.command:
            return_code = command.execute(args)
            exit(return_code)

    arg_parser.print_help()
    exit(1)
