from enum import Enum
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class MMFitMode(Enum):
    COVER = 'COVER'
    CONTAIN = 'CONTAIN'

class MMScreen(BaseModel):
    device_id: str = Field(description='Device ID')
    x_pos: int = Field(description='Screen x position')
    y_pos: int = Field(description='Screen y position')
    width: int = Field(description='Screen width', gt=0)
    height: int = Field(description='Screen height', gt=0)
    icc: Path | None = Field(description='Screen ICC location', default=None)


class MMScreenLayout:
    screens: list[MMScreen]
    min_x: int
    min_y: int
    max_x: int
    max_y: int
    total_width: int
    total_height: int

    def __init__(self, screens: list[MMScreen]):
        screens.sort(key=lambda s: (s.y_pos, s.x_pos))
        self.screens = screens
        self.min_x = min(s.x_pos for s in screens)
        self.min_y = min(s.y_pos for s in screens)
        self.max_x = max(s.x_pos + s.width for s in screens)
        self.max_y = max(s.y_pos + s.height for s in screens)
        self.total_width = int(self.max_x - self.min_x)
        self.total_height = int(self.max_y - self.min_y)


class MMImageSet(BaseModel):
    name: str = Field(description='Image name', min_length=1, default="Wallpaper %d.jpg")
    ignore_icc: bool = Field(description='Ignore --bake-icc option for this set', default=False)
    images: list[Path] = Field(description='Paths to images to use for this set', min_length=1, default=[])


class MMConfig(BaseModel):
    screens: list[MMScreen] = Field(description='Screen list', default=[])
    background_color: str = Field(description='Background color', default='black')
    default_image: Path | None = Field(description='Default image path', default=None)
    fit_mode: MMFitMode = Field(description='Image fit mode', default=MMFitMode.COVER)
    image_sets: list[MMImageSet] = Field(description='Image set list', default=[])


def load_config(config_path: Path) -> MMConfig:
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        return MMConfig.model_validate(data)
    except Exception as e:
        raise RuntimeError(f'Failed to load configuration from {config_path}') from e


def write_config(config_path: Path, data: MMConfig):
    try:
        model_dump = data.model_dump(exclude_none=False)
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(model_dump, f, sort_keys=False)
    except Exception as e:
        raise RuntimeError(f'Failed to save configuration to {config_path}') from e
