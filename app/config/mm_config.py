from enum import Enum
from pathlib import Path

import yaml
from PIL.ImageCms import ImageCmsProfile
from pydantic import BaseModel, Field, field_validator


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

    __cms_profile: ImageCmsProfile | None = None

    @property
    def cms_profile(self) -> ImageCmsProfile:
        try:
            if self.icc and self.__cms_profile is None:
                with open(self.icc, 'rb') as f:
                    self.__cms_profile = ImageCmsProfile(f)
            return self.__cms_profile
        except Exception as e:
            raise RuntimeError(f'Failed to load CMS profile from {self.icc} for screen {self.device_id}') from e


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
    file_name: str = Field(description='Image name', min_length=1, default="Wallpaper %d.jpg")
    images: list[Path] = Field(description='Paths to images to use for this set', min_length=1, default=[])

    @field_validator('images', mode='after')
    @classmethod
    def validate_images_exist(cls, v: list[Path]) -> list[Path]:
        for img in v:
            if not img.exists():
                raise ValueError(f'Image file does not exist: {img}')
        return v


class MMConfig(BaseModel):
    screens: list[MMScreen] = Field(description='Screen list', default=[])
    background_color: str = Field(description='Background color', default='black')
    default_image: Path | None = Field(description='Default image path', default=None)
    fit_mode: MMFitMode = Field(description='Image fit mode', default=MMFitMode.COVER)
    compression_quality: int = Field(description='Compression quality', default=100)
    image_sets: list[MMImageSet] = Field(description='Image set list', default=[])

    @field_validator('image_sets', mode='after')
    @classmethod
    def validate_unique_set_names(cls, v: list[MMImageSet]) -> list[MMImageSet]:
        # We need to ignore names that have the {index} keyword, as they will automatically be unique.
        unindexed_names = [s.file_name for s in v if "{index}" not in s.file_name]
        unique_unindexed_names = set(unindexed_names)
        if len(unique_unindexed_names) != len(unindexed_names):
            raise ValueError('Image set names must not contain duplicate names.')
        return v

    @field_validator('default_image', mode='after')
    @classmethod
    def validate_default_image(cls, v: Path | None) -> Path | None:
        if v is not None and not v.exists():
            raise ValueError(f'Default image file does not exist: {v}')
        return v


def load_config(config_path: Path) -> MMConfig:
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        return MMConfig.model_validate(data)
    except Exception as e:
        raise RuntimeError(f'Failed to load configuration from {config_path}') from e


def write_config(config_path: Path, data: MMConfig):
    try:
        model_dump = data.model_dump(exclude_none=False, mode='json')
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(model_dump, f, sort_keys=False)
    except Exception as e:
        raise RuntimeError(f'Failed to save configuration to {config_path}') from e
