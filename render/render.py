from io import BytesIO
from pathlib import Path

from PIL import Image
from PIL.ImageCms import ImageCmsProfile, Intent, createProfile, profileToProfile

from config import MMImageSet, MMScreenLayout, MMFitMode, MMScreen

SRGB_PROFILE = ImageCmsProfile(createProfile('sRGB'))
IMAGE_MODE = 'RGB'


def __bake_color_profile(image: Image.Image, target_profile: ImageCmsProfile):
    source_profile = SRGB_PROFILE

    if "icc_profile" in image.info:
        # Use embedded profile as source for baking
        embedded_icc_bytes = image.info.get("icc_profile")
        source_profile = ImageCmsProfile(BytesIO(embedded_icc_bytes))

    profileToProfile(
        im=image,
        inputProfile=source_profile,
        outputProfile=target_profile,
        renderingIntent=Intent.PERCEPTUAL,
        outputMode=IMAGE_MODE,
        inPlace=True
    )


def __fit_image_to_screen_cover(image: Image.Image, screen: MMScreen) -> Image.Image:
    if image.width == screen.width and image.height == screen.height:
        return image

    img_aspect = image.width / image.height
    screen_aspect = screen.width / screen.height

    if img_aspect < screen_aspect:
        target_width = screen.width
        target_height = int(screen.width / img_aspect)
    elif img_aspect > screen_aspect:
        target_width = int(screen.height * img_aspect)
        target_height = screen.height
    else:
        target_width = screen.width
        target_height = screen.height

    resampling = Image.Resampling.LANCZOS if target_width > image.width else Image.Resampling.BICUBIC
    scaled_image = image.resize((target_width, target_height), resampling)

    left_crop = (target_width - screen.width) // 2
    top_crop = (target_height - screen.height) // 2
    right_crop = left_crop + screen.width
    bottom_crop = top_crop + screen.height

    return scaled_image.crop((left_crop, top_crop, right_crop, bottom_crop))


def __fit_image_to_screen_contain(image: Image.Image, screen: MMScreen, background_color: str) -> Image.Image:
    if image.width == screen.width and image.height == screen.height:
        return image

    img_aspect = image.width / image.height
    screen_aspect = screen.width / screen.height

    if img_aspect < screen_aspect:
        target_width = int(screen.height * img_aspect)
        target_height = screen.height
    elif img_aspect > screen_aspect:
        target_height = int(screen.width / img_aspect)
        target_width = screen.width
    else:
        target_width = screen.width
        target_height = screen.height

    resampling = Image.Resampling.LANCZOS if target_width > image.width else Image.Resampling.BICUBIC
    scaled_image = image.resize((target_width, target_height), resampling)
    result = Image.new(IMAGE_MODE, (screen.width, screen.height), color=background_color)

    paste_x = (screen.width - target_width) // 2
    paste_y = (screen.height - target_height) // 2

    result.paste(scaled_image, (paste_x, paste_y))

    return result


def render_image_set(image_set: MMImageSet,
                     output_path: Path,
                     layout: MMScreenLayout,
                     default_image: Path,
                     fit_mode: MMFitMode,
                     background_color: str,
                     bake_screen_icc: bool,
                     compression_quality: int) -> None:
    base_image = Image.new(IMAGE_MODE, (layout.total_width, layout.total_height), color=background_color)

    for i, screen in enumerate(layout.screens):
        if i >= len(image_set.images):
            if default_image is None:
                break  # Leave other screen areas to background_color

            image_path = default_image
        else:
            image_path = image_set.images[i]

        image = Image.open(image_path)

        if image.mode != IMAGE_MODE:
            image = image.convert(IMAGE_MODE)

        # If bake_icc is true, we need to bake for the target screen, else we can just convert to sRGB.
        if bake_screen_icc and screen.cms_profile:
            __bake_color_profile(image, screen.cms_profile)
        else:
            __bake_color_profile(image, SRGB_PROFILE)

        img_x_pos = int(screen.x_pos - layout.min_x)
        img_y_pos = int(screen.y_pos - layout.min_y)

        match fit_mode:
            case MMFitMode.COVER:
                image = __fit_image_to_screen_cover(image, screen)
            case MMFitMode.CONTAIN:
                image = __fit_image_to_screen_contain(image, screen, background_color)

        base_image.paste(image, (img_x_pos, img_y_pos))

    # If we bake the monitor ICC's we should NOT embed the profile.
    embed_icc = None if bake_screen_icc else SRGB_PROFILE.tobytes()
    base_image.save(output_path, icc_profile=embed_icc, quality=compression_quality)
