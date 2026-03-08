from app.config.profiles import MMMonitor

BACKENDS = [
    'xrandr',
    'none'
]


def get_monitor_layout(backend: str) -> list[MMMonitor]:
    """
    Retrieves the current monitor layout based on the specified backend.

    This function dynamically selects and executes the appropriate backend implementation to fetch the active monitor configuration.
    The supported backends include 'none', which returns an empty list, and 'xrandr', which queries the X11 RandR extension for monitor information.
    Other backends are not currently supported and will raise an exception.

    :param backend: The name of the backend to use for retrieving monitor layout. Must be one of:
        - ``'none'``: Returns an empty list, indicating no monitors detected.
        - ``'xrandr'``: Uses X11 RandR extension to fetch monitor configuration.
    :return: A list of :class:`MMMonitor` objects representing the current active monitors.
             The list is empty if 'none' backend is selected or no monitors are available.
             Raises an exception for unsupported backends with a descriptive message."""
    match backend:
        case 'none':
            return []
        case 'xrandr':
            from .xrandr import get_xrandr_monitor_layout
            return get_xrandr_monitor_layout()
        case _:
            raise Exception(f'Unknown backend: {backend}')
