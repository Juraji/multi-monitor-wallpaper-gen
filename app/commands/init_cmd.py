import logging
from argparse import Namespace, ArgumentParser
from pathlib import Path

from app.config.model import MMImageSet, MMProfile
from app.config.profiles import write_profile
from app.screens import get_monitor_layout, BACKENDS
from .command import Command, SubParsersAction

logger = logging.getLogger(__name__)


class InitCommand(Command):

    def __init__(self, sub_parsers: SubParsersAction):
        super().__init__(sub_parsers, 'init', 'Detect environment and create initial configuration')

    def register_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            '--backend',
            choices=BACKENDS,
            default=BACKENDS[0],
            required=False,
            help=f'The backend used to detect monitors, set to none to not infer screen setup. Defaults to "{BACKENDS[0]}"'
        )
        parser.add_argument(
            '-f', '--force',
            action='store_true',
            default=False,
            required=False,
            help='Overwrite existing configuration file. Defaults to "False".'
        )

    def execute(self, args: Namespace) -> int:
        config_path: Path = args.configuration

        if config_path.exists():
            if not args.force:
                logger.error(f'Configuration file already exists at {config_path}, remove it before proceeding.')
                return 1
            else:
                logger.warning(f'Overwriting existing configuration file at {config_path} because of force parameter.')

        logger.info(f'Detecting screen layout using backend {args.backend}..')
        screens = get_monitor_layout(args.backend)
        logger.info(f'Found {len(screens)} screens.')

        new_config = MMProfile(
            monitors=screens,
            # Add a single example set
            image_sets=[
                MMImageSet.model_construct(
                    file_name='My wallpaper {index}.jpg',
                    images={[s.device_id]: None for s in screens})
            ]
        )

        logger.info(f'Writing config to {config_path}...')
        write_profile(config_path, new_config)
        logger.info(f'Configuration file written to {config_path}.')
        return 0
