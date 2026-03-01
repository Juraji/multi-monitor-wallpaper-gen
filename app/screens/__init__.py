from app.config.profiles import MMScreen

BACKENDS = [
    'xrandr',
    'none'
]


def get_screen_layout(backend: str) -> list[MMScreen]:
    match backend:
        case 'none':
            return []
        case 'xrandr':
            from .xrandr import get_xrandr_screen_layout
            return get_xrandr_screen_layout()
        case _:
            raise Exception(f'Unknown backend: {backend}')
