import logging
import os
from argparse import Namespace, ArgumentParser
from concurrent.futures import Future
from concurrent.futures.thread import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageCms
from PIL.ImageFile import ImageFile

from config import load_config, MMImageSet, MMScreenLayout, MMFitMode, MMScreen

logger = logging.getLogger(__name__)
SRGB_PROFILE = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB'))
IMG_MODE = 'RGB'


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


def _bake_icc(image: ImageFile, icc: Path):
    source_profile = SRGB_PROFILE

    with open(icc, 'rb') as f:
        target_profile = ImageCms.ImageCmsProfile(f)

    if "icc_profile" in image.info:
        # Use embedded profile for baking
        embedded_icc_bytes = image.info.get("icc_profile")
        source_profile = ImageCms.ImageCmsProfile(BytesIO(embedded_icc_bytes))
        target_profile = target_profile or SRGB_PROFILE

    ImageCms.profileToProfile(
        im=image,
        inputProfile=source_profile,
        outputProfile=target_profile,
        renderingIntent=ImageCms.Intent.PERCEPTUAL,
        outputMode=IMG_MODE,
        inPlace=True
    )


def _fit_image_cover(image: ImageFile, screen: MMScreen) -> ImageFile:
    img_aspect = image.width / image.height
    screen_aspect = screen.width / screen.height

    if img_aspect < screen_aspect:
        target_width, target_height = screen.width, int(screen.width / img_aspect)
    elif img_aspect > screen_aspect:
        target_width, target_height = int(screen.height * img_aspect), screen.height
    else:
        target_width, target_height = screen.width, screen.height

    left_crop = (target_width - screen.width) // 2
    top_crop = (target_height - screen.height) // 2
    right_crop = left_crop + screen.width
    bottom_crop = top_crop + screen.height

    return image.crop((left_crop, top_crop, right_crop, bottom_crop))


def _fit_image_contain(image: ImageFile, screen: MMScreen) -> ImageFile:
    raise NotImplementedError("Contain mode is not yet implemented.")


def render_image_set(image_set: MMImageSet,
                     output_path: Path,
                     layout: MMScreenLayout,
                     default_image: Path,
                     fit_mode: MMFitMode,
                     background_color: str,
                     bake_icc: bool):
    base_image = Image.new(IMG_MODE, (layout.total_width, layout.total_height), color=background_color)

    for i, screen in enumerate(layout.screens):
        if i >= len(image_set.images):
            image_path = default_image
        else:
            image_path = image_set.images[i]

        image = Image.open(image_path)

        if image.mode != IMG_MODE:
            image = image.convert(IMG_MODE)

        if bake_icc and not image_set.ignore_icc and screen.icc:
            _bake_icc(image, screen.icc)

        img_x_pos = int(screen.x_pos - layout.min_x)
        img_y_pos = int(screen.y_pos - layout.min_y)

        match fit_mode:
            case MMFitMode.COVER:
                image = _fit_image_cover(image, screen)
            case MMFitMode.CONTAIN:
                image = _fit_image_contain(image, screen)
                pass

        base_image.paste(image, (img_x_pos, img_y_pos))

    base_image.save(output_path, icc_profile=SRGB_PROFILE.tobytes())


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

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures: list[Future[None]] = []

        for set_index, image_set in enumerate(config.image_sets):
            set_out_path: Path = output_dir / image_set.name
            if set_out_path.exists():
                if not replace_images:
                    logger.info(f'Image {image_set.name} already exists, skipping generation.')
                    continue

            logger.info(f'Generating image {image_set.name}...')
            future = executor.submit(render_image_set,
                                     image_set,
                                     output_dir,
                                     screen_layout,
                                     default_image,
                                     fit_mode,
                                     background_color,
                                     bake_icc)
            futures.append(future)

        for future in futures:
            future.result()

        logger.info('Done!')
