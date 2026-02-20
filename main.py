import io
import os
from argparse import ArgumentParser, ArgumentTypeError, Namespace
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image, ImageCms
from PIL.Image import Resampling
from PIL.ImageCms import ImageCmsProfile

from screen import Screen, ScreenLayout


def parse_monitor_arg(value: str) -> Screen:
    try:
        parts = value.replace('x', '+').split('+')
        if len(parts) != 4:
            raise ValueError

        return Screen(
            width=int(parts[0]),
            height=int(parts[1]),
            x_pos=int(parts[2]),
            y_pos=int(parts[3])
        )
    except Exception:
        raise ArgumentTypeError(f"Monitor must be in format WidthxHeight+OffsetX+OffsetY, got {value}.")


def parse_images_arg(value: str) -> dict[str, list[Path]]:
    try:
        with open(value, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip() != '']

        if not lines:
            raise ValueError("File is empty or contains only empty lines. Must start with a title like '# [title]'")

        if not lines[0].startswith('#'):
            raise ValueError(f"First non-empty line must be a title, like '# [title]'. Found: '{lines[0]}'")

        image_sets = {}
        current_title = None

        for line in lines:
            if line.startswith('#'):
                set_no = len(image_sets) + 1
                title = line[1:].strip().replace('%d', str(set_no))
                if not title:
                    raise ValueError(f"Set '{title}' has no title, each set must have a unique title")
                if title in image_sets:
                    raise ValueError(f'Duplicate title in images list "{title}"')
                current_title = title
                image_sets[title] = []
            else:
                if current_title is None:
                    raise ValueError(f"Path specified without preceding title: '{line}'")
                p = Path(line)
                if not p.exists():
                    raise ValueError(f"Path '{line}' does not exist")
                image_sets[current_title].append(p)

        for title, paths in image_sets.items():
            if len(paths) == 0:
                raise ValueError(f"Set '{title}' has no images. Each set must contain at least one path")

        return image_sets

    except FileNotFoundError:
        raise ArgumentTypeError(f"Images file {value} not found.")
    except ValueError as pe:
        raise ArgumentTypeError(f"Error parsing {value}: {pe}.")


def render_image_set(images: list[Path],
                     layout: ScreenLayout,
                     background: str,
                     target_profile: ImageCmsProfile | None,
                     outpath: Path):
    base_image = Image.new('RGB', (layout.total_width, layout.total_height), color=background)
    srgb_profile = ImageCmsProfile(ImageCms.createProfile("sRGB"))

    for i, s in enumerate(layout.screens):
        if i >= len(images):
            break  # No more images to use
        image_path = images[i]
        image = Image.open(image_path)  # Could fail if path is not an image, but we'll just let the error bubble up.

        if image.mode != 'RGB':
            image = image.convert('RGB')

        if "icc_profile" in image.info:
            embedded_icc_bytes = image.info.get("icc_profile")
            embedded_profile = ImageCms.ImageCmsProfile(io.BytesIO(embedded_icc_bytes))
            target_profile = target_profile or srgb_profile

            ImageCms.profileToProfile(
                im =image,
                inputProfile=embedded_profile,
                outputProfile=target_profile,
                renderingIntent=ImageCms.Intent.PERCEPTUAL,
                outputMode="RGB",
                inPlace=True
            )
        elif not target_profile is None:
            ImageCms.profileToProfile(
                im=image,
                inputProfile=srgb_profile,
                outputProfile=target_profile,
                renderingIntent=ImageCms.Intent.PERCEPTUAL,
                outputMode="RGB",
                inPlace=True
            )

        img_x_pos = int(s.x_pos - layout.min_x)
        img_y_pos = int(s.y_pos - layout.min_y)

        img_aspect = image.width / image.height
        screen_aspect = s.width / s.height

        if img_aspect < screen_aspect:
            new_width = s.width
            new_height = int(s.width / img_aspect)
        elif img_aspect > screen_aspect:
            new_width = int(s.height * img_aspect)
            new_height = s.height
        else:
            new_width = s.width
            new_height = s.height

        image = image.resize((new_width, new_height), Resampling.LANCZOS)

        left_crop = (new_width - s.width) // 2
        top_crop = (new_height - s.height) // 2
        right_crop = left_crop + s.width
        bottom_crop = top_crop + s.height

        image = image.crop((left_crop, top_crop, right_crop, bottom_crop))
        base_image.paste(image, (img_x_pos, img_y_pos))

    base_image.save(outpath, icc_profile=srgb_profile.tobytes())


def main(options: Namespace):
    if not options.output_dir.exists():
        options.output_dir.mkdir(parents=True)

    if not options.monitor:
        from screen import get_screen_layout_from_compositor

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
    print(f'Screens: {len(screen_layout.screens)}, '
          f'layout width: {screen_layout.total_width}, '
          f'layout height: {screen_layout.total_height}.')
    if target_profile:
        print(f'Target color profile: {target_profile}')
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
