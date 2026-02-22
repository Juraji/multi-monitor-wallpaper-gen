import logging
import os
from argparse import Namespace, ArgumentParser
from pathlib import Path

from config import write_config, MMConfig, MMImageSet
from screens import get_screen_layout

logger = logging.getLogger(__name__)

def setup_parser(parser: ArgumentParser):
    parser.add_argument(
        '--backend',
        choices=['xrandr', 'none'],
        default='xrandr',
        required=False,
        help=f'The backend used to detect monitors, set to none to not infer screen setup. Defaults to "xrandr"'
    )
    parser.add_argument(
        '-f', '--force',
        action='store_true',
        default=False,
        required=False,
        help='Overwrite existing configuration file. Defaults to "False".'
    )

def init_cmd(args: Namespace):
    config_path: Path = args.configuration

    if config_path.exists():
        if not args.force:
            logger.error(f'Configuration file already exists at {config_path}, remove it before proceeding.')
            exit(1)
        else:
            logger.warning(f'Overwriting existing configuration file at {config_path} because of force parameter.')

    logger.info(f'Detecting screen layout using backend {args.backend}..')
    screens = get_screen_layout(args.backend)
    logger.info(f'Found {len(screens)} screens.')

    new_config = MMConfig(
        screens=screens,
        # Add a single example set
        image_sets=[MMImageSet(images=['/path/to/image-1.png', '/path/to/image-2.png'])]
    )

    logger.info(f'Writing config to {config_path}...')
    write_config(config_path, new_config)
    logger.info(f'Configuration file written to {config_path}.')
