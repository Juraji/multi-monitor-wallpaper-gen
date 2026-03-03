from textual.visual import VisualType
from textual.widgets import Label


class MMHeading(Label):
    DEFAULT_CSS = """
    MMHeading {
        color: $primary;
        text-style: bold;
        padding-bottom: 1;
    }
    """

    def __init__(self, content: VisualType):
        super().__init__(content=content)
