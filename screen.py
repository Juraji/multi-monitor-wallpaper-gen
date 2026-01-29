import platform
import subprocess


class Screen:
    width: int
    height: int
    x_pos: int
    y_pos: int

    def __init__(self, width: int, height: int, x_pos: int, y_pos: int):
        self.width = width
        self.height = height
        self.x_pos = x_pos
        self.y_pos = y_pos

    def __repr__(self):
        return f"Screen(width={self.width}, height={self.height}, x_pos={self.x_pos}, y_pos={self.y_pos})"


class ScreenLayout:
    screens: list[Screen]
    min_x: int
    min_y: int
    max_x: int
    max_y: int
    total_width: int
    total_height: int

    def __init__(self, screens: list[Screen]):
        screens.sort(key=lambda s: (s.y_pos, s.x_pos))
        self.screens = screens
        self.min_x = min(s.x_pos for s in screens)
        self.min_y = min(s.y_pos for s in screens)
        self.max_x = max(s.x_pos + s.width for s in screens)
        self.max_y = max(s.y_pos + s.height for s in screens)
        self.total_width = int(self.max_x - self.min_x)
        self.total_height = int(self.max_y - self.min_y)


def get_screen_layout_from_compositor() -> ScreenLayout:
    if platform.system() == "Linux":
        return __get_xrandr_screens()
    else:
        raise UnableToGetScreenLayoutException("Unsupported OS or display compositor")


def __get_xrandr_screens() -> ScreenLayout:
    """
    Retrieve the list of active screens using xrandr command.

    :raises RuntimeError: If the xrandr command fails.
    :return: List of Screen objects representing active screens.
    """

    # example:$ xrandr --listactivemonitors
    # Monitors: 2
    #  0: +*DP-4 5120/930x2160/390+0+0  DP-4
    #  1: +HDMI-0 1440/1024x2560/1920+5120+0  HDMI-0

    result = subprocess.run(
        ['xrandr', '--listactivemonitors'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True)

    if result.returncode != 0:
        raise UnableToGetScreenLayoutException(f"Command failed with error: {result.stderr}")

    lines = result.stdout.splitlines()
    screens: list[Screen] = []

    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue

        dim_str = line.split()[2]
        if not 'x' in dim_str:
            continue

        parts = dim_str.replace('x', '+').split('+')
        if len(parts) != 4:
            continue

        try:
            width = int(parts[0].split('/')[0])
            height = int(parts[1].split('/')[0])
            x_pos = int(parts[2])
            y_pos = int(parts[3])
        except ValueError:
            continue

        screens.append(Screen(width, height, x_pos, y_pos))

    if len(screens) == 0:
        raise UnableToGetScreenLayoutException("No screens found using xrandr.")
    return ScreenLayout(screens)


class UnableToGetScreenLayoutException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
