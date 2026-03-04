from pathlib import Path

from rich.repr import auto as rich_repr_auto, Result as RichResult
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Label, Button
from textual_fspicker import FileOpen, Filters

IMAGE_FILTERS = Filters(
    ('PNG', lambda f: f.suffix.lower() == '.png'),
    ('JPG', lambda f: f.suffix.lower() in ('.jpg', '.jpeg')),
    ('GIF', lambda f: f.suffix.lower() == '.gif'),
)


class MMFileSelect(Horizontal):
    DEFAULT_CSS = """
    MMFileSelect {
        width: 100%;
        height: auto;
    }
    
    #selected-path-label {
        width: 1fr;
        border: tall $border-blurred;
        border-right: none;
        text-align: left;
        content-align: left middle;
        background: $surface;
        padding: 0 1;
        text-wrap: nowrap;
        text-overflow: ellipsis;
    }
    """

    @rich_repr_auto
    class Changed(Message):
        def __init__(self, select: 'MMFileSelect', value: Path | None):
            super().__init__()
            self.select = select
            self.value = value

        def __rich_repr__(self) -> RichResult:
            yield self.select
            yield self.value

        @property
        def control(self) -> 'MMFileSelect':
            return self.select

    path: Path | None = reactive(None)
    filters: Filters | None = None
    selected_path_label: Label | None = None
    clear_path_button: Button | None = None

    def __init__(self,
                 path: Path | None,
                 filters: Filters | None = None,
                 id: str | None = None):
        super().__init__(id=id)
        self.path = path
        self.filters = filters

    def compose(self) -> ComposeResult:
        self.selected_path_label = Label(id='selected-path-label', content=str(self.path))
        yield self.selected_path_label

        self.clear_path_button = Button(id='clear-path-button', label='Clear', disabled=not self.path)
        yield self.clear_path_button
        yield Button(id='select-path-button', label='Select')

    def watch_path(self, path: Path):
        if self.selected_path_label:
            self.selected_path_label.content = str(path)
        if self.clear_path_button:
            self.clear_path_button.disabled = not path

    @on(Button.Pressed, '#clear-path-button')
    def on_clear_path(self):
        self.path = None
        self.post_message(self.Changed(self, None))

    @on(Button.Pressed, '#select-path-button')
    async def on_select_path(self):
        if self.path:
            if self.path.is_file():
                root = self.path.parent
            else:
                root = self.path
        else:
            root = "."

        selector = FileOpen(location=root, filters=self.filters)
        self.path = await self.app.push_screen_wait(selector)
        self.post_message(self.Changed(self, self.path))
