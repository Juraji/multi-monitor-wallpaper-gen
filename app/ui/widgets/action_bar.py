from textual.containers import Horizontal
from textual.reactive import reactive


class MMActionBar(Horizontal):
    """A horizontal container for 1..n buttons."""

    dock_bottom: bool = reactive(False)

    DEFAULT_CSS = """
    MMActionBar {
        height: auto;
        width: 100%;
        padding-top: 1;
        align-horizontal: right;
        
        &.compact {
            padding-top: 0;
        }
    }

    MMActionBar Button {
        margin-left: 1;
    }
    """

    def __init__(self, dock_bottom: bool = True, compact: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.dock_bottom = dock_bottom
        if compact:
            self.add_class('compact')

    def watch_dock_bottom(self, dock_bottom: bool):
        if dock_bottom:
            self.styles.dock = "bottom"
        else:
            self.styles.dock = None
