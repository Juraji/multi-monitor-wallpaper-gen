from pathlib import Path

from PIL.ImageCms import ImageCmsProfile, createProfile

PROFILES_DIR = Path("./profiles")
GENERATED_OUT_DIR = Path("./generated")
ALLOWED_EXTENSIONS = ["png", "jpg"]
STANDARD_SRGB_PROFILE = ImageCmsProfile(createProfile('sRGB'))
TARGET_IMAGE_MODE = 'RGB'