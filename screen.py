import subprocess


class Screen:
    width: int
    height: int
    x_pos: int
    y_pos: int

    def __init__(self, width, height, x_pos, y_pos):
        self.width = width
        self.height = height
        self.x_pos = x_pos
        self.y_pos = y_pos

    def __repr__(self):
        return f"Screen(width={self.width}, height={self.height}, x_pos={self.x_pos}, y_pos={self.y_pos})"


def get_xrandr_screens() -> list[Screen]:
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
        raise RuntimeError(f"Command failed with error: {result.stderr}")

    lines = result.stdout.splitlines()
    screens: list[Screen] = []

    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue

        dim_str = line.split()[2]
        if not 'x' in dim_str:
            continue

        x_index = dim_str.index('x')
        plus1_index = dim_str.index('+', x_index)
        plus2_index = dim_str.index('+', plus1_index + 1)

        try:
            width = int(dim_str[:x_index].split('/')[0])
            height = int(dim_str[x_index + 1:plus1_index].split('/')[0])
            x_pos = int(dim_str[plus1_index + 1:plus2_index])
            y_pos = int(dim_str[plus2_index + 1:])
        except ValueError:
            continue

        screens.append(Screen(width, height, x_pos, y_pos))

    screens.sort(key=lambda s: (s.y_pos, s.x_pos))
    return screens
