import subprocess

from config import MMScreen


def _xrandr_list_active_monitors() -> list[tuple[str, int, int, int, int]]:
    """
    Retrieves a list of currently active monitors along with their dimensions and positions using the `xrandr` command.

    This function parses the output of the ``xrandr --listactivemonitors`` command to extract monitor information,
    including display location (identifier), x-position, y-position, width, and height in pixels.
    The result is returned as a list of tuples where each tuple contains the monitor identifier followed by
    its coordinates and dimensions.

    :return: List of active monitors represented as tuples containing:
        - Monitor identifier (string)
        - X-coordinate position (integer)
        - Y-coordinate position (integer)
        - Width in pixels (integer)
        - Height in pixels (integer)

    :raises Exception: If the ``xrandr`` command fails to execute or returns a non-zero exit code,
                      containing the error message from stderr.
    """
    # example:$ xrandr --listactivemonitors
    # Monitors: 2
    #  0: +*DP-4 5120/930x2160/390+0+0  DP-4
    #  1: +HDMI-0 1440/1024x2560/1920+5120+0  HDMI-0
    result = subprocess.run(
        ['xrandr', '--listactivemonitors'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True)

    if result.returncode != 0:
        raise Exception(f"Failed to list active monitors using xrandr: {result.stderr}")

    lines = result.stdout.splitlines()
    screens: list[tuple[str, int, int, int, int]] = []

    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue

        line_parts = line.split()
        dim_str = line_parts[2]
        if 'x' not in dim_str:
            continue
        location = line_parts[3]

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

        screens.append((location, x_pos, y_pos, width, height))

    return screens


def _xrandr_list_color_profiles() -> dict[str, str]:
    """
    Retrieves a mapping of XRandR display devices to their associated ICC color profiles using the `colormgr` command.

    This function executes the `colormgr get-devices-by-kind display` command to fetch device information,
    parsing the output to extract object paths (XRandR identifiers) and corresponding ICC profile paths.
    The result is returned as a dictionary where keys are XRandR device identifiers and values are
    the associated color profile file paths.

    The function ensures proper handling of locale settings by setting ``LC_ALL=C`` to guarantee consistent
    output formatting. If the command execution fails, an exception is raised with the error message from stderr.

    .. note::
        Requires the `colormgr` tool to be installed and available in the system PATH.
    """
    result = subprocess.run(
        ['colormgr', 'get-devices-by-kind', 'display'],
        env={"LC_ALL": "C"},  # Make sure output is in standard locale
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True)

    if result.returncode != 0:
        raise Exception(f"Failed to get color profiles: {result.stderr}")

    lines = result.stdout.splitlines()
    devices: dict[str, str] = {}
    current_xrandr: str | None = None
    current_profile: str | None = None

    for line in lines:
        line = line.strip()

        if line.startswith('Object Path:'):
            if current_xrandr and current_profile:
                devices[current_xrandr] = current_profile
            current_xrandr = None
            current_profile = None
            continue

        if line.startswith('Metadata:') and '=' in line:
            current_xrandr = line.split('=')[1]
            continue

        if current_profile is None and line.startswith('/') and line.endswith('.icc'):
            current_profile = line

    if current_xrandr and current_profile:
        devices[current_xrandr] = current_profile

    return devices


def get_xrandr_screen_layout() -> list[MMScreen]:
    try:
        active_monitors = _xrandr_list_active_monitors()

        if not active_monitors:
            raise RuntimeError("No active monitors detected by xrandr")

        color_profiles = _xrandr_list_color_profiles()

        return [
            MMScreen(
                device_id=device_id,
                x_pos=x_pos,
                y_pos=y_pos,
                width=width,
                height=height,
                icc=color_profiles.get(device_id, None)
            )
            for device_id, x_pos, y_pos, width, height in active_monitors
        ]
    except Exception as e:
        raise RuntimeError(f"Failed to get screen layout: {str(e)}") from e
