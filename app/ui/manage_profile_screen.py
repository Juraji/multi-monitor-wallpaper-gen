from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Header, Static


class MMManageProfileScreen(Screen):
    CSS = """
    #content {
        align: center middle;
        width: 60%;
        height: 50%;
        border: solid $accent;
        padding: 2 4;
    }
    #profile-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 2;
    }
    #placeholder {
        color: $text-muted;
        margin-bottom: 2;
    }
    """

    def __init__(self, profile_path: Path | None):
        super().__init__()
        self.profile_path = profile_path

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="content"):
            yield Static(id="profile-title")
            yield Static("Profile management coming soon...", id="placeholder")
            yield Button("← Back to Home", id="back-home", variant="default")

    def on_mount(self):
        title = self.profile_path.stem if self.profile_path else "New Profile"
        self.query_one("#profile-title", Static).update(f"Profile: {title}")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "back-home":
            self.app.pop_screen()
