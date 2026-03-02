from typing import Iterable

from textual.app import App, SystemCommand
from textual.screen import Screen

from app.ui.home_screen import MMHomeScreen
from app.ui.manage_profile_screen import MMManageProfileScreen


class MMApp(App):
    TITLE = "MM Wallpaper Generator"
    SCREENS = {"home": MMHomeScreen, "manage": MMManageProfileScreen}

    def on_mount(self):
        self.push_screen(MMHomeScreen())