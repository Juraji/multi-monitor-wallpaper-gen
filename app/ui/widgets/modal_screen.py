from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Label, Button

from app.ui.widgets.action_bar import MMActionBar


class MMModalScreen(ModalScreen):
    DEFAULT_CSS = """
    MMModalScreen {
        align: center middle;
    }
    
    #modal-container {
        width: 80;
        height: auto;
        padding: 0 1;
        border: thick $surface-darken-1 80%;
        background: $background;
    }
    
    #modal-title {
        color: $primary;
        text-style: bold;
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        Binding(key='escape', action='cancel_modal', description='Cancel Modal'),
    ]

    modal_title = reactive("")
    confirm_button_label = reactive("")
    cancel_button_label = reactive("")

    def __init__(self,
                 modal_title: str = 'Modal',
                 confirm_button_label: str = "Confirm",
                 cancel_button_label: str = "Cancel"):
        super().__init__()
        self.modal_title = modal_title
        self.confirm_button_label = confirm_button_label
        self.cancel_button_label = cancel_button_label

    def compose(self) -> ComposeResult:
        with Container(id='modal-container'):
            yield Label(self.modal_title, id='modal-title')
            yield from self.compose_content()
            with MMActionBar(dock_bottom=True):
                yield Button(label=self.cancel_button_label, id='cancel-button', variant='error')
                yield Button(label=self.confirm_button_label, id='confirm-button', variant='primary')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "cancel-button":
                result = self.handle_cancel()
            case "confirm-button":
                result = self.handle_confirm()
            case _:
                raise NotImplementedError(f"Unknown button pressed with id {event.button.id}.")

        self.dismiss(result)

    def action_cancel_modal(self):
        result = self.handle_cancel()
        self.dismiss(result)

    # noinspection PyMethodMayBeStatic
    def compose_content(self) -> ComposeResult:
        """Override in subclasses."""
        raise NotImplementedError("Override compose_content()")

    # noinspection PyMethodMayBeStatic
    def handle_cancel(self) -> Any:
        return None

    def handle_confirm(self) -> Any:
        """Override in subclasses."""
        raise NotImplementedError("Override handle_confirm()")
