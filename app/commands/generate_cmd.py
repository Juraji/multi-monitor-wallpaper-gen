import logging
import os
from argparse import Namespace, ArgumentParser
from concurrent.futures import Future
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path

from app.config.constants import GENERATED_OUT_DIR
from app.config.profiles import load_profile, MMFitMode, MMScreenLayout, MMImageSet
from app.render.render import render_image_set

logger = logging.getLogger(__name__)


def setup_parser(parser: ArgumentParser):
    parser.add_argument(
        '-o', '--output-dir',
        default=GENERATED_OUT_DIR,
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
    parser.add_argument(
        '-i', '--start-index',
        type=int,
        default=1,
        help='The starting index when using the "{index}" key in wallpaper names. Defaults to 1.'
    )


def generate_cmd(args: Namespace):
    logger.info(f'Loading config from {args.configuration}...')
    profile = load_profile(args.configuration)
    output_dir: Path = args.output_dir
    replace_images: bool = args.replace
    bake_icc: bool = args.bake_icc
    max_workers: int = args.max_workers
    start_index: int = args.start_index
    default_image: Path | None = profile.default_image
    fit_mode: MMFitMode = profile.fit_mode
    background_color: str = profile.background_color
    compression_quality = profile.compression_quality

    logger.info(f"""\
Configuration loaded:
  Screens: {len(profile.screens)}
  Image sets: {len(profile.image_sets)}
  Replace images: {'yes' if replace_images else 'no'}
  Max workers: {max_workers}
  Bake ICC: {'yes' if bake_icc else 'no'}
  Start index: {start_index}
  Default image: {default_image}
  Fit mode: {fit_mode}
  Background color: {background_color}
  Compression quality: {compression_quality}
    """)

    if not output_dir.exists():
        logging.info(f'Creating directory {output_dir}...')
        output_dir.mkdir(parents=True)

    screen_layout = MMScreenLayout(profile.screens)

    def image_set_handler(image_set: MMImageSet, index: int):
        file_name = image_set.file_name.format(index=index)
        set_out_path: Path = output_dir / file_name
        if set_out_path.exists():
            if not replace_images:
                logger.info(f'Image {file_name} already exists, skipping generation.')
                return

        logger.info(f'Generating image {file_name}...')
        render_image_set(image_set,
                         set_out_path,
                         screen_layout,
                         default_image,
                         fit_mode,
                         background_color,
                         bake_icc,
                         compression_quality)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures: list[Future[None]] = []

        for (i, s) in enumerate(profile.image_sets):
            i = start_index + i
            future = executor.submit(image_set_handler, s, i)
            futures.append(future)

        for future in futures:
            future.result()

        logger.info('Done!')
