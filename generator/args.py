from argparse import ArgumentTypeError
from pathlib import Path

from generator.screen import Screen


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
