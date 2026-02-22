import logging
import os
from argparse import Namespace, ArgumentParser
from concurrent.futures import Future
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path

from config import load_config, MMImageSet, MMScreenLayout, MMFitMode
from render import render_image_set

logger = logging.getLogger(__name__)


def setup_parser(parser: ArgumentParser):
    parser.add_argument(
        '-o', '--output-dir',
        default='./generated',
        type=Path,
        help='The directory to output the generated images to. Defaults to "./generated"'
    )
    parser.add_argument(
        '-r', '--replace',
        action='store_true',
        default=False,
        help='Replace images in the target directory. Defaults to "False".'
    )
    parser.add_argument(
        '--bake-icc',
        action='store_true',
        default=False,
        help='Bake monitor ICC profiles (Gnome users will want this). Defaults to "False".'
    )
    parser.add_argument(
        '-w', '--max-workers',
        type=int,
        default=max(4, os.cpu_count()),
        help='The maximum number of workers to use. Defaults to the cpu core count with a minimum of 4.'
    )


def generate_cmd(args: Namespace):
    logger.info(f'Loading config from {args.configuration}...')
    config = load_config(args.configuration)
    output_dir: Path = args.output_dir
    replace_images: bool = args.replace
    bake_icc: bool = args.bake_icc
    max_workers: int = args.max_workers
    default_image: Path | None = config.default_image
    fit_mode: MMFitMode = config.fit_mode
    background_color: str = config.background_color

    logger.info(f'Configuration loaded:\n'
                f'  Screens: {len(config.screens)}\n'
                f'  Image sets: {len(config.image_sets)}\n'
                f'  Default image: {config.default_image}\n'
                f'  Replace images: {'yes' if replace_images else 'no'}\n'
                f'  Max workers: {max_workers}\n'
                f'  Bake ICC: {'yes' if bake_icc else 'no'}')

    if not output_dir.exists():
        logging.info(f'Creating directory {output_dir}...')
        output_dir.mkdir(parents=True)

    screen_layout = MMScreenLayout(config.screens)

    def image_set_handler(image_set: MMImageSet):
        set_out_path: Path = output_dir / image_set.file_name
        if set_out_path.exists():
            if not replace_images:
                logger.info(f'Image {image_set.file_name} already exists, skipping generation.')
                return

        logger.info(f'Generating image {image_set.file_name}...')
        render_image_set(image_set, set_out_path, screen_layout, default_image, fit_mode, background_color, bake_icc)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures: list[Future[None]] = []

        for s in config.image_sets:
            future = executor.submit(image_set_handler, s)
            futures.append(future)

        for future in futures:
            future.result()

        logger.info('Done!')
