from typing import Any

from textual.app import ComposeResult
from textual.widgets import Static

from app.ui.widgets.modal_screen import MMModalScreen


class MMConfirmModal(MMModalScreen):

    def __init__(self,
                 message: str,
                 modal_title: str = 'Confirm Action',
                 confirm_button_label: str = 'Yes',
                 cancel_button_label: str = 'No'):
        super().__init__(modal_title=modal_title,
                         confirm_button_label=confirm_button_label,
                         cancel_button_label=cancel_button_label)
        self.message = message

    def compose_content(self) -> ComposeResult:
        yield Static(content=self.message)

    def handle_cancel(self) -> Any:
        return False

    def handle_confirm(self) -> Any:
        return True
