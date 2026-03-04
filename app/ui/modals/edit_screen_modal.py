from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.validation import Length, Integer
from textual.widgets import Label, Input

from app.config.profiles import MMScreen
from app.ui.widgets.file_select import MMFileSelect, ICC_FILTERS
from app.ui.widgets.modal_screen import MMModalScreen


class MMEditScreenModal(MMModalScreen):
    CSS = """
    .inline-input {
        width: 1fr;
    }
    
    Horizontal {
        height: auto;
    }
    """

    device_id_input: Input
    position_x_input: Input
    position_y_input: Input
    width_input: Input
    height_input: Input
    icc_input: MMFileSelect

    def __init__(self, screen: MMScreen | None):
        super().__init__(modal_title="Edit Screen",
                         confirm_button_label="Apply",
                         disable_confirm_on_init=True)
        self.mm_screen = screen

    def compose_content(self) -> ComposeResult:
        yield Label("Device ID:")
        self.device_id_input = Input(id='device-id-input',
                                     value=self.mm_screen.device_id,
                                     validators=Length(minimum=1))
        yield self.device_id_input

        yield Label("Position (x,y):")
        with Horizontal():
            self.position_x_input = Input(id='position-x-input',
                                          classes='inline-input',
                                          value=str(self.mm_screen.x_pos),
                                          validators=Integer())
            yield self.position_x_input
            self.position_y_input = Input(id='position-y-input',
                                          classes='inline-input',
                                          value=str(self.mm_screen.y_pos),
                                          validators=Integer())
            yield self.position_y_input

        yield Label("Size (width,height):")
        with Horizontal():
            self.width_input = Input(id='width-input',
                                     classes='inline-input',
                                     value=str(self.mm_screen.width),
                                     validators=Integer(minimum=1))
            yield self.width_input
            self.height_input = Input(id='height-input',
                                      classes='inline-input',
                                      value=str(self.mm_screen.height),
                                      validators=Integer(minimum=1))
            yield self.height_input

        yield Label("Monitor ICC:")
        self.icc_input = MMFileSelect(id='icc-input',
                                      path=self.mm_screen.icc,
                                      filters=ICC_FILTERS)
        yield self.icc_input

    @on(Input.Changed)
    def on_any_input(self):
        self.confirm_button_disabled = \
            not self.device_id_input.is_valid or \
            not self.position_x_input.is_valid or \
            not self.position_y_input.is_valid or \
            not self.width_input.is_valid or \
            not self.height_input.is_valid

        if self.confirm_button_disabled: return

        self.mm_screen.device_id = self.device_id_input.value
        self.mm_screen.x_pos = int(self.position_x_input.value)
        self.mm_screen.y_pos = int(self.position_y_input.value)
        self.mm_screen.width = int(self.width_input.value)
        self.mm_screen.height = int(self.height_input.value)

    @on(MMFileSelect.Changed, '#icc-input')
    def on_icc_changed(self, e: MMFileSelect.Changed):
        self.mm_screen.icc = e.value

    def handle_confirm(self) -> Any:
        return self.mm_screen
