from app.config.profiles import MMMonitor

BACKENDS = [
    'xrandr',
    'none'
]


def get_monitor_layout(backend: str) -> list[MMMonitor]:
    match backend:
        case 'none':
            return []
        case 'xrandr':
            from .xrandr import get_xrandr_monitor_layout
            return get_xrandr_monitor_layout()
        case _:
            raise Exception(f'Unknown backend: {backend}')
