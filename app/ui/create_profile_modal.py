from typing import Any

from textual.app import ComposeResult
from textual.widgets import Label, Input, Select

from app.config.constants import PROFILES_DIR
from app.config.profiles import MMProfile, write_profile
from app.screens import get_screen_layout
from app.ui.widgets.modal_screen import MMModalScreen


class MMCreateProfileModal(MMModalScreen):
    def __init__(self) -> None:
        super().__init__(modal_title='Create New Profile', confirm_button_label='Create Profile')

    def compose_content(self) -> ComposeResult:
        yield Label('Profile Name:')
        yield Input(id='profile-name', type='text')
        yield Label('Detect screens:')
        yield Select(id='detect-screens', options=[
            ('Skip detection', 'none'),
            ('Use XRandR', 'xrandr'),
        ], value='xrandr')

    def handle_confirm(self) -> Any:
        name = self.query_one('#profile-name', Input).value
        detect_backend = self.query_one('#detect-screens', Select).value

        profile_path = PROFILES_DIR / f'{name}.yaml'
        screens = get_screen_layout(detect_backend)
        p = MMProfile(screens=screens)

        write_profile(profile_path, p)

        return profile_path
