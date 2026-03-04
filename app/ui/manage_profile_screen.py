from pathlib import Path
from typing import cast

from PIL.ImageColor import colormap
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal
from textual.screen import Screen
from textual.validation import Integer
from textual.widgets import Header, Footer, Label, Input, Select, Button, ListItem, ListView

from app.config.profiles import MMProfile, MMFitMode, write_profile, MMScreen
from app.ui.modals.edit_screen_modal import MMEditScreenModal
from app.ui.widgets.action_bar import MMActionBar
from app.ui.widgets.file_select import MMFileSelect, IMAGE_FILTERS
from app.ui.widgets.heading import MMHeading
from app.ui.widgets.panel import MMPanel


class _SettingsPanel(MMPanel):
    CSS = """
    _SettingsPanel {
        height: auto;
    }
    """

    profile: MMProfile

    def __init__(self, profile: MMProfile):
        super().__init__()
        self.profile = profile

    def compose(self) -> ComposeResult:
        yield MMHeading('Settings:')

        color_options = [(k.upper(), k) for k in colormap]
        yield Label(content='Background color:')
        yield Select(id='background-color-select',
                     options=color_options,
                     value=self.profile.background_color)

        yield Label(content='Default Image:')
        yield MMFileSelect(id='default-image-select',
                           path=self.profile.default_image,
                           filters=IMAGE_FILTERS)

        fit_mode_options = [(e.name, e) for e in MMFitMode]
        yield Label(content='Fit Mode:')
        yield Select(id='fit-mode-select',
                     options=fit_mode_options,
                     value=self.profile.fit_mode)

        yield Label(content='Compression Quality:')
        yield Input(id='compression-quality-input',
                    value=str(self.profile.compression_quality),
                    validators=Integer(0, 100))

    @on(Select.Changed, '#background-color-select')
    def on_background_color_select(self, e: Select.Changed):
        self.profile.background_color = e.value

    @on(MMFileSelect.Changed, '#default-image-select')
    def on_default_image_select(self, e: MMFileSelect.Changed):
        self.profile.default_image = e.value

    @on(Select.Changed, '#fit-mode-select')
    def on_fit_mode_select(self, e: Select.Changed):
        self.profile.fit_mode = e.value

    @on(Input.Changed, '#compression-quality-input')
    def on_compression_quality_input(self, e: Input.Changed):
        if not e.input.is_valid: return
        self.profile.compression_quality = int(e.value)


class ScreenItem(ListItem):
    def __init__(self, screen: MMScreen):
        super().__init__()
        self.mm_screen = screen

    def compose(self) -> ComposeResult:
        s = self.mm_screen
        yield Label(content=f'{s.device_id} - {s.width}x{s.height} @ {s.x_pos},{s.y_pos}')


class _ScreensPanel(MMPanel):
    profile: MMProfile
    screen_list_view: ListView | None

    def __init__(self, profile: MMProfile):
        super().__init__()
        self.profile = profile
        self.screen_list_view = None

    def compose(self) -> ComposeResult:
        yield MMHeading('Screens:')
        self.screen_list_view = ListView(id="screen-list")
        yield self.screen_list_view
        with MMActionBar():
            yield Button(id='add-screen-button', label='Add Screen')

    def on_mount(self):
        self.render_screen_items()

    def render_screen_items(self):
        self.screen_list_view.clear()
        if not len(self.profile.screens):
            self.screen_list_view.append(ListItem(Label('No screens defined!'), disabled=True))
        for s in self.profile.screens:
            self.screen_list_view.append(ScreenItem(s))

    @on(ListView.Selected, "#screen-list")
    def on_screen_list_select(self, e: ListView.Selected):
        index = e.index
        item = cast(ScreenItem, e.item)
        modal = MMEditScreenModal(item.mm_screen)

        async def on_edit_screen_modal_dismiss(result: MMScreen | None):
            if result is None: return
            self.profile.screens[index] = result
            self.render_screen_items()

        self.app.push_screen(modal, callback=on_edit_screen_modal_dismiss)

    @on(Button.Pressed, '#add-screen-button')
    def on_add_screen(self):
        # TODO: Create and open modal with fields to add a screen.
        pass


class _ImageSetsPanel(MMPanel):
    profile: MMProfile

    def __init__(self, profile: MMProfile):
        super().__init__()
        self.profile = profile

    def compose(self) -> ComposeResult:
        yield MMHeading('Image Sets:')
        yield Label(content='Not yet implemented')
        with MMActionBar():
            yield Button(id='add-image-set-button', label='Add Set', variant='primary')

    @on(Button.Pressed, '#add-image-set-button')
    def on_add_image_set(self):
        # TODO: Create and open modal with fields to add an image set.
        pass

    def validate(self) -> bool:
        return True


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
    """

    profile_path: Path
    profile_name: str
    profile: MMProfile

    settings_panel: _SettingsPanel
    screens_panel: _ScreensPanel
    image_sets_panel: _ImageSetsPanel

    BINDINGS = [
        Binding(key='escape', action='back_home', description='Back Home'),
        Binding(key='ctrl+s', action='save_profile', description='Save Profile'),
        Binding(key='ctrl+r', action='rename_profile', description='Rename Profile'),
        Binding(key='F12', action='render_images', description='Render Images'),
    ]

    def __init__(self, profile_path: Path, profile: MMProfile):
        super().__init__()
        self.profile_path = profile_path
        self.profile_name = profile_path.stem
        self.profile = profile

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer(show_command_palette=False)
        with Horizontal():
            with Vertical(id='left-panel'):
                self.settings_panel = _SettingsPanel(self.profile)
                yield self.settings_panel

                self.screens_panel = _ScreensPanel(self.profile)
                yield self.screens_panel

            with Vertical(id='right-panel'):
                self.image_sets_panel = _ImageSetsPanel(self.profile)
                yield self.image_sets_panel

    def on_mount(self):
        self.sub_title = f"Profile: {self.profile_name}"

    def action_back_home(self):
        self.app.pop_screen()

    def action_save_profile(self):
        async def _write_profile():
            write_profile(self.profile_path, self.profile)
            self.notify(f'Profile {self.profile_name} saved!')

        self.run_worker(_write_profile, exclusive=True)

    def action_rename_profile(self):
        # TODO: Special action, create and open a modal to rename this profile (rename the file)
        pass

    def action_render_images(self):
        # TODO: Send this profile off to render_image_set, some kind of progress display would be nice!
        pass
