from pathlib import Path
from typing import Any, cast

from attr.validators import disabled
from textual import on, events
from textual.app import ComposeResult
from textual.message import Message
from textual.validation import Length
from textual.widgets import Label, Input, ListView, ListItem, Button
from textual_fspicker import FileOpen

from app.config.constants import ALLOWED_EXTENSIONS
from app.config.profiles import MMImageSet
from app.ui.validators.ends_with import EndsWith
from app.ui.widgets.action_bar import MMActionBar
from app.ui.widgets.file_select import IMAGE_FILTERS
from app.ui.widgets.modal_screen import MMModalScreen


class _ImageListItem(ListItem):
    class RemoveImage(Message):
        def __init__(self, image_path: Path, index: int):
            super().__init__()
            self.image_path = image_path
            self.index = index

    def __init__(self, image_path: Path, index: int):
        super().__init__()
        self.image_path = image_path
        self.index = index

    def compose(self) -> ComposeResult:
        yield Label(f'{self.index + 1}: {self.image_path}')
        with MMActionBar(compact=True):
            yield Button('Remove', id='remove-image', compact=True)

    @on(Button.Pressed, '#remove-image')
    def on_remove(self):
        self.post_message(self.RemoveImage(self.image_path, self.index))


class MMEditImageSetModal(MMModalScreen):
    CSS = """
    #image-list-view {
        margin-top: 1;
        height: auto;
        min-height: 3;
    }
    """

    set_name_input: Input
    image_list_view: ListView

    def __init__(self, set_index: int | None, image_set: MMImageSet | None):
        if set_index:
            title = f'Edit Image Set ({set_index + 1})'
        else:
            title = f'New Image Set'

        super().__init__(modal_title=title,
                         confirm_button_label='Apply',
                         disable_confirm_on_init=True)
        self.image_set = image_set

    def compose_content(self) -> ComposeResult:
        yield Label('Set name:')
        self.set_name_input = Input(id='set-name-input',
                                    value=self.image_set.file_name,
                                    validators=[Length(minimum=1), EndsWith(ALLOWED_EXTENSIONS)])
        yield self.set_name_input

        self.image_list_view = ListView(id='image-list-view')
        yield self.image_list_view

        with MMActionBar(dock_bottom=False):
            yield Button(label='Add Image', id='add-image')

    def on_mount(self):
        for i, p in enumerate(self.image_set.images):
            self.image_list_view.append(_ImageListItem(p, i))

        self.check_list_empty()

    def handle_confirm(self) -> Any:
        images = [cast(_ImageListItem, e).image_path for e in self.image_list_view.children]
        self.image_set.images = images
        return self.image_set

    @on(Input.Changed, '#set-name-input')
    def handle_set_name_change(self, e: Input.Changed) -> Any:
        if not e.input.is_valid: return
        self.image_set.file_name = e.input.value
        self.check_validity()

    @on(Button.Pressed, '#add-image')
    def on_add_image(self):
        def on_modal_dismiss(e: Path):
            next_idx = len(self.image_list_view)
            self.image_list_view.append(_ImageListItem(e, next_idx))

        selector = FileOpen(filters=IMAGE_FILTERS)
        self.app.push_screen(selector, callback=on_modal_dismiss)

    @on(_ImageListItem.RemoveImage)
    def handle_remove(self, e: _ImageListItem.RemoveImage) -> Any:
        self.image_list_view.pop(e.index)
        self.check_validity()
        self.check_list_empty()

    def check_validity(self):
        self.confirm_button_disabled = \
            not self.set_name_input.is_valid \
            or len(self.image_list_view) == 0

    def check_list_empty(self):
        if not len(self.image_list_view):
            self.image_list_view.append(ListItem(Label('No images defined'), disabled=True))
