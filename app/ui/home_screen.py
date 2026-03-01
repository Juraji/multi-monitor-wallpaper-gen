from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, ListView, ListItem, Static, Header

from app.config.profiles import list_profiles
from app.ui.manage_profile_screen import MMManageProfileScreen


class MMHomeScreen(Screen):
    CSS = """
    #left-panel {
        width: 60%;
        height: 100%;
        padding: 1;
    }
    #right-panel {
        width: 40%;
        height: 100%;
        background: $surface-darken-1;
        padding: 1;
    }
    
    #profile-list-title {
        margin-bottom: 1;
    }
    #profile-list {
        height: 1fr;
    }
    #empty-state {
        height: 1fr;
        color: $text-muted;
        content-align: center middle;
    }
    
    #actions-panel {
        dock: bottom;
        height: auto;
        margin-top: 1;
        align-horizontal: right;
    }

    #instructions-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    #instructions-text {
        color: $text;
    }
    """

    available_profiles: list[Path] = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="left-panel"):
                yield Static("Select a profile", id="profile-list-title")
                yield ListView(id="profile-list")
                yield Static("No profiles yet", id="empty-state")
                with Horizontal(id="actions-panel"):
                    yield Button(
                        "Create New Profile", id="create-new-profile", variant="primary"
                    )
            with Vertical(id="right-panel"):
                yield Static("What To Do", id="instructions-title")
                yield Static(id="instructions-text")

    def on_mount(self):
        self.available_profiles = list_profiles()

        list_view = self.query_one("#profile-list", ListView)
        empty_state = self.query_one("#empty-state", Static)
        instructions = self.query_one("#instructions-text", Static)

        list_view.clear()
        for profile_path in self.available_profiles:
            profile_name = profile_path.stem
            item = ListItem(Static(profile_name))
            list_view.append(item)

        has_profiles = bool(self.available_profiles)
        empty_state.display = not has_profiles
        list_view.display = has_profiles

        if has_profiles:
            instructions.update(
                "Select an existing profile to use, or create a new one to get started."
            )
        else:
            instructions.update(
                "Welcome! Create your first profile to get started with multi-monitor wallpaper generation.\n\n"
                "A profile stores your monitor configuration, images, and settings."
            )

    def on_list_view_selected(self, event: ListView.Selected):
        match event.list_view.id:
            case "profile-list":
                selected_index = event.list_view.index
                if selected_index is not None:
                    path = self.available_profiles[selected_index]
                    self.app.push_screen(MMManageProfileScreen(path))

    def on_button_pressed(self, event: Button.Pressed):
        match event.button.id:
            case "create-new-profile":
                self.app.push_screen(MMManageProfileScreen(None))
