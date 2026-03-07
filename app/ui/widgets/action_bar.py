from textual.containers import Horizontal
from textual.reactive import reactive


class MMActionBar(Horizontal):
    """A horizontal container for 1..n buttons."""

    DEFAULT_CSS = """
    MMActionBar {
        height: auto;
        width: 100%;
        padding-top: 1;
        align-horizontal: right;
        
        &.docker-bottom {
            dock: bottom;
        }
        
        &.compact {
            padding-top: 0;
        }
        
        Button {
            margin-left: 1;
        }
    }
    """

    def __init__(self, dock_bottom: bool = True, compact: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.dock_bottom = dock_bottom
        if dock_bottom:
            self.add_class('docker-bottom')
        if compact:
            self.add_class('compact')
