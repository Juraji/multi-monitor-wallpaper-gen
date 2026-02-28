# AGENTS.md - Agent Guidelines for multi-monitor-wallpaper-gen

## Project Overview

Python tool for generating combined wallpaper images for multi-monitor setups. Detects monitors via `xrandr` and maps images with color profile handling.

---

## CRITICAL: Always Use Virtual Environment

**NEVER** run Python, pip, pytest, ruff, or any other Python commands without first activating the virtual environment.

```bash
# ALWAYS activate the venv first
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

- Never install packages globally (e.g., `pip install --user` or system-wide pip)
- Never run `python` without the venv activated
- If you need to add dependencies, install them with `pip install -r requirements.txt` inside the activated venv
- Scripts that call Python tools should explicitly activate the venv or use `.venv/bin/python` directly

---

## Commands

### Running
```bash
# Initialize configuration (detect monitors)
python main.py init

# Generate wallpapers from config
python main.py generate

# Use start.sh for automatic venv setup
./start.sh init
./start.sh generate
```

### Linting
```bash
ruff check .
ruff check . --fix
ruff format .
```

### Testing
```bash
pytest                           # all tests
pytest tests/test_screen.py      # single file
pytest tests/test_screen.py::test_function_name  # single function
pytest -k "pattern"              # by pattern
pytest -v                        # verbose
```

## Code Style

- Use Python 3.12+ features (type hints with `|`, match/case)
- Add type hints to all functions
- Keep lines under 100 chars
- Avoid unnecessary comments

### Imports (3 sections, blank lines between)
1. Standard library
2. Third-party
3. Local

```python
import os
from pathlib import Path
from PIL import Image
from config import MMConfig
```

### Naming
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `SCREAMING_SNAKE_CASE`
- Private methods: `_prefix`

### Type Hints
Use `X | None` instead of `Optional[X]`:
```python
def func(images: list[Path], profile: Path | None) -> None:
```

### Error Handling
- Use specific exceptions (`ValueError`, `ArgumentTypeError`)
- Descriptive messages

### Threading
Use context manager:
```python
with ThreadPoolExecutor(max_workers=max(4, os.cpu_count())) as executor:
    for future in futures:
        future.result()
```

### Testing
- Test files: `tests/test_<module>.py`
- Test functions: `test_<description>`
- Test edge cases and errors

## Structure
```
.
├── main.py                      # CLI entry point
├── commands/                    # CLI commands
│   ├── __init__.py
│   ├── init_cmd.py             # Monitor detection & config init
│   └── generate_cmd.py          # Wallpaper generation
├── config/                      # Configuration handling
│   ├── __init__.py
│   └── mm_config.py             # Pydantic models & YAML load/save
├── screens/                     # Screen detection backends
│   ├── __init__.py
│   └── xrandr.py                # xrandr backend
├── config.yaml                  # Configuration file
├── requirements.txt
└── tests/                       # (to be added)
```

## Dependencies
- `pillow` - image processing
- `pydantic` - config validation
- `PyYAML` - YAML configuration
- `ruff` - linting
- `pytest` - testing
