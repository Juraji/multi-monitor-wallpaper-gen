from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal, Container, Right
from textual.screen import Screen
from textual.widgets import Header, Footer, Label, Input, Select, Button

from app.config.profiles import MMProfile, load_profile, MMFitMode


class MMManageProfileScreen(Screen):
    CSS = """
    #left-panel {
        width: 40%;
        height: 100%;
        padding: 1;
    }
    #right-panel {
        width: 60%;
        height: 100%;
        padding: 1;
    }
    
    .panel {
        background: $surface-darken-1;
        padding: 1;
        margin-bottom: 1;
    }
    
    .panel:last-child {
        margin-bottom: 0;
    }
    
    .heading {
        color: $primary;
        text-style: bold;
        padding-bottom: 1;
    }
    
    .actions {
        width: 100%;
        dock: bottom;
    }
    
    #settings-panel {
        height: auto;
    }
    """

    profile_path: Path
    profile_name: str
    profile: MMProfile

    background_color_input: Input
    default_image_input: Input
    fit_mode_select: Select
    compression_quality_input: Input

    BINDINGS = [
        Binding(key='escape', action='back_home', description='Back Home'),
        Binding(key='ctrl+s', action='save_profile', description='Save Profile'),
        Binding(key='ctrl+r', action='rename_profile', description='Rename Profile'),
        Binding(key='F12', action='render_images', description='Render Images'),
    ]

    def __init__(self, profile_path: Path):
        super().__init__()
        self.profile_path = profile_path
        self.profile_name = profile_path.stem

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer(show_command_palette=False)
        with Horizontal():
            with Vertical(id='left-panel'):
                with Container(id='settings-panel', classes='panel'):
                    yield Label(content='Settings:', classes='heading')
                    yield Label(content='Background color:')
                    self.background_color_input = Input(id='background-color-input')
                    yield self.background_color_input

                    yield Label(content='Default Image:')
                    self.default_image_input = Input(id='default-image-input')
                    yield self.default_image_input

                    yield Label(content='Fit Mode:')
                    self.fit_mode_select = Select(id='fit-mode-select', options=[(e.name, e) for e in MMFitMode])
                    yield self.fit_mode_select

                    yield Label(content='Compression Quality:')
                    self.compression_quality_input = Input(id='compression-quality-input')
                    yield self.compression_quality_input

                with Container(id='screens-panel', classes='panel'):
                    yield Label(content='Screens:', classes='heading')
                    yield Label(content='Not yet implemented')
                    with Right(id='screens-actions', classes='actions'):
                        yield Button(id='add-screen-button', label='Add Screen')

            with Vertical(id='right-panel'):
                with Container(id='image-sets-panel', classes='panel'):
                    yield Label(content='Image Sets:', classes='heading')
                    yield Label(content='Not yet implemented')
                    with Right(id='image-sets-actions', classes='actions'):
                        yield Button(id='add-image-set-button', label='Add Set', variant='primary')

    def on_mount(self):
        self.sub_title = f"Profile: {self.profile_name}"
        self.run_worker(self.load_profile, exclusive=True)

    @on(Button.Pressed, '#add-screen-button')
    def on_add_screen(self):
        # TODO: Create and open modal with fields to add a screen.
        pass

    @on(Button.Pressed, '#add-image-set-button')
    def on_add_image_set(self):
        # TODO: Create and open modal with fields to add an image set.
        pass

    def action_back_home(self):
        self.app.pop_screen()

    def action_save_profile(self):
        # TODO: Collect all various bits, update self.profile and save it
        pass

    def action_rename_profile(self):
        # TODO: Special action, create and open a modal to rename this profile (rename the file)
        pass

    def action_render_images(self):
        # TODO: Send this profile off to render_image_set, some kind of progress display would be nice!
        pass

    async def load_profile(self):
        p = load_profile(self.profile_path)
        self.profile = p
        self.background_color_input.value = p.background_color
        self.default_image_input.value = str(p.default_image)
        self.fit_mode_select.value = p.fit_mode
        self.compression_quality_input.value = str(p.compression_quality)
