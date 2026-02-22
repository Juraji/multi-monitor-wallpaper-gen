import subprocess

from config import MMScreen


def _xrandr_list_active_monitors() -> list[tuple[str, int, int, int, int]]:
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
    # example:$ LC_ALL=C colormgr get-devices-by-kind display
    # Object Path:   /org/freedesktop/ColorManager/devices/xrandr_LG_Electronics_LG_ULTRAWIDE_212NTDV15498_user_1000
    # Owner:         user
    # ... More keys ...
    # Device ID:     xrandr-LG Electronics-LG ULTRAWIDE-212NTDV15498
    # Profile 1:     icc-2e397f485ab3e1909dd35a707b41cd63
    #                /home/user/.local/share/icc/edid-82d1fd7ad80989b63bc944302e6f05d4.icc
    # Profile 2:     icc-5e686704735bec23eef25e2b5764fb50
    #                /home/user/.local/share/icc/edid-86cbf7a1b0f23089549785f54466d0b4.icc
    # Profile 3:     icc-25298bd3fdd6cb8f947a822d8547cac0
    #                /home/user/.local/share/icc/edid-95191d98a22a5c981e761954871d0e3b.icc
    # Metadata:      OutputEdidMd5=95191d98a22a5c981e761954871d0e3b
    # Metadata:      OutputPriority=primary
    # Metadata:      XRANDR_name=DP-4

    result = subprocess.run(
        ['colormgr', 'get-devices-by-kind', 'display'],
        env={"LC_ALL": "C"},  # Make sure output is in standard locale
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True)

    if result.returncode != 0:
        raise Exception(f"Failed to list active monitors using xrandr: {result.stderr}")

    lines = result.stdout.splitlines()
    devices: dict[str, str] = {}

    current_xrandr_name: str | None = None
    current_profile: str | None = None
    for line in reversed(lines):
        line = line.strip()

        if 'XRANDR_name' in line:
            current_xrandr_name = line.split('XRANDR_name=')[1]

        if current_xrandr_name and '/home' in line:
            current_profile = line

        if current_xrandr_name and current_profile:
            devices[current_xrandr_name] = current_profile

        if not line:
            current_xrandr_name = None
            current_profile = None

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
