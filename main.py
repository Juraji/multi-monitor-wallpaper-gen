import os
from argparse import ArgumentParser, Namespace
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import ImageCms
from PIL.ImageCms import ImageCmsProfile

from generator.args import parse_monitor_arg, parse_images_arg
from generator.render import render_image_set
from generator.screen import ScreenLayout


def main(options: Namespace):
    if not options.output_dir.exists():
        options.output_dir.mkdir(parents=True)

    if not options.monitor:
        from generator.screen import get_screen_layout_from_compositor

        try:
            screen_layout = get_screen_layout_from_compositor()
        except Exception as e:
            print(f"Error: No monitors specified and failed to detect them: {e}")
            exit(1)
    else:
        screen_layout = ScreenLayout(options.monitor)

    target_profile: ImageCmsProfile | None = None
    if args.target_icc:
        with open(args.target_icc, 'rb') as f:
            target_profile = ImageCms.ImageCmsProfile(f)

    print(f'Rendering {len(options.images)} images to {options.output_dir}...')
    print(repr(screen_layout))
    if target_profile:
        print(f'Target color profile: "{target_profile.profile.profile_description}"')
    print()

    # Sets the max thread count to CPU count with a minimum of 4
    max_workers = max(4, os.cpu_count())
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []

        for set_title, images in options.images.items():
            outpath = options.output_dir / f'{set_title}.{options.type}'
            if not options.replace and outpath.exists():
                print(f"Output file {outpath.stem} already exists. Skipping.")
            else:
                print(f'Rendering image "{set_title}" of {len(images)} sub-images to {outpath}...')
                future = executor.submit(render_image_set,
                                         images,
                                         screen_layout,
                                         options.background,
                                         target_profile,
                                         outpath)
                futures.append(future)

        for future in futures:
            future.result()

    print("Done.")


if __name__ == '__main__':
    # Parse arguments
    arg_parser = ArgumentParser(description='Batch generate multi-monitor wallpapers')
    arg_parser.add_argument(
        '-i', '--images',
        default='./images.txt',
        type=parse_images_arg,
        help='The TXT file with paths to the images to use. One image per line, separated by "# [title]" per image set. Defaults to "./images.txt".')
    arg_parser.add_argument(
        '-o', '--output-dir',
        default='./generated',
        type=Path,
        help='The directory to output the generated images to. Defaults to "./generated"'
    )
    arg_parser.add_argument(
        '-m', '--monitor',
        action='append',
        type=parse_monitor_arg,
        required=False,
        help='The coordinates of the monitor(s). Can be specified multiple times. Defaults to all monitors reported by the desktop compositor.'
    )
    arg_parser.add_argument(
        '-b', '--background',
        default='black',
        help='The background color of the wallpaper for areas without images. Defaults to "black".'
    )
    arg_parser.add_argument(
        '-t', '--type',
        default='jpg',
        choices=['jpg', 'png'],
        help='The type of output images. Defaults to "jpg".'
    )
    arg_parser.add_argument(
        '-r', '--replace',
        action='store_true',
        default=False,
        help='Replace images in the target directory. Defaults to "False".'
    )
    arg_parser.add_argument(
        '-c', '--target-icc',
        type=Path,
        required=False,
        help='ICC profile to convert images to. Defaults to standard sRGB.'
    )

    args = arg_parser.parse_args()
    main(args)
