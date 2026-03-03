from textual.containers import Container


class MMPanel(Container):
    DEFAULT_CSS = """
    MMPanel {
        background: $surface-darken-1;
        padding: 1;
        margin-bottom: 1;
    }
    
    MMPanel:last-child {
        margin-bottom: 0;
    }
    """