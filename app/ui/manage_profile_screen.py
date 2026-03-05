from pathlib import Path
from typing import cast

from PIL.ImageColor import colormap
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal
from textual.message import Message
from textual.screen import Screen
from textual.validation import Integer
from textual.widgets import Header, Footer, Label, Input, Select, Button, ListItem, ListView

from app.config.profiles import MMProfile, MMFitMode, write_profile, MMMonitor
from app.ui.modals.confirm_modal import MMConfirmModal
from app.ui.modals.edit_screen_modal import MMEditMonitorModal
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


class _MonitorItem(ListItem):
    class EditMonitor(Message):
        def __init__(self, monitor: MMMonitor, index: int):
            super().__init__()
            self.monitor = monitor
            self.index = index

    class RemoveMonitor(Message):
        def __init__(self, monitor: MMMonitor, index: int):
            super().__init__()
            self.monitor = monitor
            self.index = index

    def __init__(self, monitor: MMMonitor, index: int):
        super().__init__()
        self.monitor = monitor
        self.index = index

    def compose(self) -> ComposeResult:
        m = self.monitor
        label = f'{m.device_id} - {m.width}x{m.height} @ {m.x_pos},{m.y_pos}'
        yield Label(content=label)
        with MMActionBar(compact=True):
            yield Button('Edit', id='edit-monitor', compact=True)
            yield Button('Remove', id='remove-monitor', compact=True)

    @on(Button.Pressed, '#edit-monitor')
    def on_edit_pressed(self, e: Button.Pressed):
        self.post_message(self.EditMonitor(self.monitor, self.index))

    @on(Button.Pressed, '#remove-monitor')
    def on_remove_pressed(self, e: Button.Pressed):
        self.post_message(self.RemoveMonitor(self.monitor, self.index))


class _MonitorsPanel(MMPanel):
    profile: MMProfile
    monitor_list_view: ListView | None

    def __init__(self, profile: MMProfile):
        super().__init__()
        self.profile = profile
        self.monitor_list_view = None

    def compose(self) -> ComposeResult:
        yield MMHeading('Monitors:')
        self.monitor_list_view = ListView(id="monitor-list")
        yield self.monitor_list_view
        with MMActionBar():
            yield Button(id='add-monitor-button', label='Add Monitor')

    def on_mount(self):
        self.render_monitor_items()

    def render_monitor_items(self):
        self.monitor_list_view.clear()
        if not len(self.profile.monitors):
            self.monitor_list_view.append(ListItem(Label('No screens defined!'), disabled=True))
        for i, s in enumerate(self.profile.monitors):
            self.monitor_list_view.append(_MonitorItem(s, i))

    @on(_MonitorItem.EditMonitor)
    def on_edit_monitor(self, e: _MonitorItem.EditMonitor):
        index = e.index
        modal = MMEditMonitorModal(e.monitor)

        async def on_edit_monitor_modal_dismiss(result: MMMonitor | None):
            if result is None: return
            self.profile.monitors[index] = result
            self.render_monitor_items()
            self.notify('Monitor updated!')

        self.app.push_screen(modal, callback=on_edit_monitor_modal_dismiss)

    @on(_MonitorItem.RemoveMonitor)
    def on_remove_monitor(self, e: _MonitorItem.RemoveMonitor):
        async def on_confirm_modal_dismiss(result: bool):
            if not result: return
            del self.profile.monitors[e.index]
            self.render_monitor_items()
            self.notify(f'Monitor "{e.monitor.device_id}" removed!')

        confirm = MMConfirmModal('Are you sure you want to remove this monitor?')
        self.app.push_screen(confirm, callback=on_confirm_modal_dismiss)

    @on(Button.Pressed, '#add-monitor-button')
    def on_add_monitor(self):
        async def on_edit_monitor_modal_dismiss(result: MMMonitor | None):
            if result is None: return
            self.profile.monitors.append(result)
            self.render_monitor_items()

        new_monitor = MMMonitor(device_id='New Monitor',
                                x_pos=0,
                                y_pos=0,
                                width=1920,
                                height=1080)
        modal = MMEditMonitorModal(new_monitor)
        self.app.push_screen(modal, callback=on_edit_monitor_modal_dismiss)


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
    screens_panel: _MonitorsPanel
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

                self.screens_panel = _MonitorsPanel(self.profile)
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
