from pathlib import Path
from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.widgets import Label, Input, Select

from app.config.constants import PROFILES_DIR
from app.config.profiles import MMProfile, write_profile
from app.screens import get_screen_layout
from app.ui.widgets.modal_screen import MMModalScreen


class MMCreateProfileModal(MMModalScreen):
    _detect_screens_options = [
        ('Skip detection', 'none'),
        ('Use XRandR', 'xrandr'),
    ]

    _profile_name_input: Input
    _detect_screens_input: Select
    _existing_profile_names: list[str]

    def __init__(self, existing_profiles: list[Path]):
        super().__init__(modal_title='Create New Profile',
                         confirm_button_label='Create Profile',
                         disable_confirm_on_init=True)

        self._existing_profile_names = [p.stem.lower() for p in existing_profiles]

    def compose_content(self) -> ComposeResult:
        yield Label('Profile Name:')
        self._profile_name_input = Input(id='profile-name', type='text')
        yield self._profile_name_input
        yield Label('Detect screens:')
        self._detect_screens_input = Select(id='detect-screens',
                                            options=self._detect_screens_options,
                                            value='xrandr')
        yield self._detect_screens_input

    def handle_confirm(self) -> Any:
        name = self._profile_name_input.value
        detect_backend = self._detect_screens_input.value

        profile_path = PROFILES_DIR / f'{name}.yaml'
        screens = get_screen_layout(detect_backend)
        p = MMProfile(screens=screens)

        write_profile(profile_path, p)

        return profile_path, p

    @on(Input.Changed, '#profile-name')
    def on_profile_name_changed(self, event: Input.Changed):
        v = event.value.strip().lower()
        self.confirm_button_disabled = not v or v in self._existing_profile_names
