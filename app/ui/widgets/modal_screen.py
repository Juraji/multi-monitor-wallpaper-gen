from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Label, Button

from app.ui.widgets.action_bar import MMActionBar
from app.ui.widgets.heading import MMHeading


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
        color: $text-accent;
        text-style: bold;
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        Binding(key='escape', action='cancel_modal', description='Cancel Modal'),
    ]

    confirm_button_disabled = reactive(False)

    def __init__(self,
                 modal_title: str = 'Modal',
                 confirm_button_label: str = "Confirm",
                 cancel_button_label: str = "Cancel",
                 disable_confirm_on_init: bool = False):
        super().__init__()
        self._confirm_button = None

        self.modal_title = modal_title
        self.confirm_button_label = confirm_button_label
        self.cancel_button_label = cancel_button_label
        self.confirm_button_disabled = disable_confirm_on_init

    def compose(self) -> ComposeResult:
        with Container(id='modal-container'):
            yield MMHeading(self.modal_title)
            yield from self.compose_content()
            with MMActionBar():
                yield Button(label=self.cancel_button_label, id='cancel-button', variant='error')
                self._confirm_button = Button(label=self.confirm_button_label, id='confirm-button', variant='primary',
                                              disabled=self.confirm_button_disabled)
                yield self._confirm_button

    @on(Button.Pressed, '#confirm-button')
    def on_confirm(self):
        result = self.handle_confirm()
        self.dismiss(result)

    @on(Button.Pressed, '#cancel-button')
    def on_cancel(self):
        result = self.handle_cancel()
        self.dismiss(result)

    def action_cancel_modal(self):
        result = self.handle_cancel()
        self.dismiss(result)

    def watch_confirm_button_disabled(self, disabled: bool):
        if self._confirm_button:
            self._confirm_button.disabled = disabled

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
