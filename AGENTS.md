# AGENTS.md - Agent Guidelines for multi-monitor-wallpaper-gen

## Project Overview

Python tool for generating combined wallpaper images for multi-monitor setups. Detects monitors via `xrandr` and maps images with color profile handling.

## Environment Setup

**IMPORTANT**: Always use `.venv` when running Python code.

```bash
source .venv/bin/activate
pip install -r requirements.txt
pip install ruff pytest
```

## Commands

### Running
```bash
python main.py
python main.py -i images.txt -o ./generated -m 1920x1080+0+0 -m 1920x1080+1920+0 -t png -b white
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
from screen import Screen
```

### Naming
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `SCREAMING_SNAKE_CASE`
- Private methods: `_prefix`

### Type Hints
Use `X | None` instead of `Optional[X]`:
```python
def func(images: list[Path], profile: ImageCmsProfile | None) -> None:
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
├── main.py
├── screen.py
├── images.txt
├── requirements.txt
├── generated/
└── tests/
```

## Dependencies
- `pillow` - image processing
- `python-icc` - ICC color profiles
- `ruff` - linting
- `pytest` - testing
