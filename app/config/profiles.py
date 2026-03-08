from pathlib import Path

import yaml

from .constants import PROFILES_DIR
from .model import MMProfile


class MMProfileLoadSaveException(Exception):
    pass


def list_profiles() -> list[Path]:
    return sorted(PROFILES_DIR.glob("*.yaml"))


def load_profile(config_path: Path) -> MMProfile:
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        return MMProfile.model_validate(data)
    except Exception as e:
        raise MMProfileLoadSaveException(f'Failed to load configuration from {config_path}: {e}') from e


def write_profile(config_path: Path, data: MMProfile):
    try:
        model_dump = data.model_dump(exclude_none=False, mode='json')
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(model_dump, f, sort_keys=False)
    except Exception as e:
        raise MMProfileLoadSaveException(f'Failed to save configuration to {config_path}') from e
