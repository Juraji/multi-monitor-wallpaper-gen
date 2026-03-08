import subprocess

from app.config.profiles import MMMonitor


def _xrandr_list_active_monitors() -> list[tuple[str, int, int, int, int]]:
    """
    Enumerate the active monitors reported by :program:`xrandr` and return a
    structured representation of their properties.

    The function executes ``xrandr --listactivemonitors`` and parses its output.
    Each monitor is represented as a tuple containing:

    * The monitor identifier string (e.g., ``"DP-4"`` or ``"HDMI-0"``).
    * The x coordinate of the monitor’s top‑left corner in pixels.
    * The y coordinate of the monitor’s top‑left corner in pixels.
    * The width of the monitor in pixels.
    * The height of the monitor in pixels.

    :Returns:
        A list of tuples.  Each tuple holds the location string, x and y
        coordinates, width, and height for one active monitor.

    :Raises:
        Exception: If ``xrandr`` fails to run or returns a non‑zero exit code,
        the function raises an exception containing the command’s error
        message.
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
    Return a dictionary mapping XRANDR device names to their active ICC profile paths.

    The function executes the ``colormgr`` command line tool to query
    display devices of kind *display*.  Each output block is parsed for an
    ``XRANDR_name`` metadata entry and the first file path ending in
    ``.icc`` that appears within the block.  The device name and its
    corresponding profile path are stored as a key/value pair in the result
    dictionary.

    If the command exits with a non‑zero return code, an :class:`Exception`
    is raised containing the captured error message.

    :return: A dictionary where each key is the XRANDR display identifier
       (e.g. ``"DP-1"``) and the value is the absolute path to its active
       ICC profile file.  An empty dictionary indicates that no profiles
       were found or the command produced no output.
    :raises Exception: If the ``colormgr`` subprocess fails to execute or
       returns a non‑zero exit status, an exception containing the error
       message from standard error is raised.
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

        if line.startswith('Metadata:') and 'XRANDR_name' in line:
            current_xrandr = line.split('=')[1]
            continue

        if current_profile is None and line.startswith('/') and line.endswith('.icc'):
            current_profile = line

    if current_xrandr and current_profile:
        devices[current_xrandr] = current_profile

    return devices


def get_xrandr_monitor_layout() -> list[MMMonitor]:
    try:
        active_monitors = _xrandr_list_active_monitors()

        if not active_monitors:
            raise RuntimeError("No active monitors detected by xrandr")

        color_profiles = _xrandr_list_color_profiles()

        return [
            MMMonitor(
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
