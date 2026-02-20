import io
from pathlib import Path

from PIL import Image, ImageCms
from PIL.Image import Resampling, Image
from PIL.ImageCms import ImageCmsProfile

from generator.screen import ScreenLayout, Screen

SRGB_PROFILE = ImageCmsProfile(ImageCms.createProfile('sRGB'))
IMG_MODE = 'RGB'


def _bake_icc(image: Image, target_profile: ImageCmsProfile | None = None):
    source_profile = SRGB_PROFILE

    if "icc_profile" in image.info:
        # Use embedded profile for baking
        embedded_icc_bytes = image.info.get("icc_profile")
        source_profile = ImageCms.ImageCmsProfile(io.BytesIO(embedded_icc_bytes))
        target_profile = target_profile or SRGB_PROFILE

    if target_profile:
        ImageCms.profileToProfile(
            im=image,
            inputProfile=source_profile,
            outputProfile=target_profile,
            renderingIntent=ImageCms.Intent.PERCEPTUAL,
            outputMode=IMG_MODE,
            inPlace=True
        )


def _fit_image_to_screen(image: Image, screen: Screen) -> tuple[int, int]:
    img_aspect = image.width / image.height
    screen_aspect = screen.width / screen.height

    if img_aspect < screen_aspect:
        return screen.width, int(screen.width / img_aspect)
    elif img_aspect > screen_aspect:
        return int(screen.height * img_aspect), screen.height
    else:
        return screen.width, screen.height


def render_image_set(images: list[Path],
                     layout: ScreenLayout,
                     background: str,
                     target_profile: ImageCmsProfile | None,
                     outpath: Path):
    base_image = Image.new(IMG_MODE, (layout.total_width, layout.total_height), color=background)

    for i, screen in enumerate(layout.screens):
        if i >= len(images):
            break  # No more images to use
        image_path = images[i]
        image = Image.open(image_path)  # Could fail if path is not an image, but we'll just let the error bubble up.

        if image.mode != IMG_MODE:
            image = image.convert(IMG_MODE)

        _bake_icc(image, target_profile)

        img_x_pos = int(screen.x_pos - layout.min_x)
        img_y_pos = int(screen.y_pos - layout.min_y)
        new_width, new_height = _fit_image_to_screen(image, screen)

        image = image.resize((new_width, new_height), Resampling.LANCZOS)

        left_crop = (new_width - screen.width) // 2
        top_crop = (new_height - screen.height) // 2
        right_crop = left_crop + screen.width
        bottom_crop = top_crop + screen.height

        image = image.crop((left_crop, top_crop, right_crop, bottom_crop))
        base_image.paste(image, (img_x_pos, img_y_pos))

    base_image.save(outpath, icc_profile=SRGB_PROFILE.tobytes())
