from io import BytesIO
from pathlib import Path

from PIL import Image
from PIL.ImageCms import ImageCmsProfile, Intent, profileToProfile

from app.config.constants import STANDARD_SRGB_PROFILE, TARGET_IMAGE_MODE
from app.config.profiles import MMMonitor, MMImageSet, MMDesktopLayout, MMFitMode


def __bake_color_profile(image: Image.Image, target_profile: ImageCmsProfile):
    """
    Bake the color profile into an image by converting it from its source
    ICC profile to the specified target profile. If the image contains an
    embedded ICC profile, that profile is used; otherwise a standard sRGB
    profile is applied. The conversion modifies the Pillow Image object in
    place so subsequent operations use the baked color data.

    :param image: The Pillow Image instance whose color profile will be baked.
    :param target_profile: The ICC profile to which the image should be converted.

    :return: None. The image is modified in place and no value is returned.
    """
    source_profile = STANDARD_SRGB_PROFILE

    if "icc_profile" in image.info:
        # Use embedded profile as source for baking
        embedded_icc_bytes = image.info.get("icc_profile")
        source_profile = ImageCmsProfile(BytesIO(embedded_icc_bytes))

    profileToProfile(
        im=image,
        inputProfile=source_profile,
        outputProfile=target_profile,
        renderingIntent=Intent.PERCEPTUAL,
        outputMode=TARGET_IMAGE_MODE,
        inPlace=True
    )


def __fit_image_to_screen_centered(image: Image.Image, monitor: MMMonitor, background_color: str) -> Image.Image:
    """
    Fit an image onto a monitor-sized canvas, centering it and filling the
    remaining area with a background color.

    :param image: The source image to be placed on the result canvas.
    :param monitor: Monitor information providing width and height.
    :param background_color: Color used for the background of the resulting
       image.
    :return: A new Image.Image instance with dimensions matching the
       monitor, containing the original image centered over the specified
       background color.
    """
    result = Image.new(TARGET_IMAGE_MODE, (monitor.width, monitor.height), color=background_color)

    paste_x = (monitor.width - image.width) // 2
    paste_y = (monitor.height - image.height) // 2
    result.paste(image, (paste_x, paste_y))

    return result


def __fit_image_to_screen_cover(image: Image.Image, monitor: MMMonitor) -> Image.Image:
    """
    Fit an image to cover a monitor screen while preserving its aspect ratio.
    The image is first scaled so that it completely covers the target resolution,
    then centered and cropped to match the monitor’s exact dimensions.

    :param image: The source :class:`PIL.Image.Image` to be resized and cropped.
    :param monitor: An :class:`MMMonitor` instance providing ``width`` and
        ``height`` attributes for the desired output size.
    :return: A new :class:`PIL.Image.Image` that exactly matches the monitor’s
        resolution, with any excess area centered and removed.
    """
    img_aspect = image.width / image.height
    screen_aspect = monitor.width / monitor.height

    if img_aspect < screen_aspect:
        target_width = monitor.width
        target_height = int(monitor.width / img_aspect)
    elif img_aspect > screen_aspect:
        target_width = int(monitor.height * img_aspect)
        target_height = monitor.height
    else:
        target_width = monitor.width
        target_height = monitor.height

    resampling = Image.Resampling.LANCZOS if target_width > image.width else Image.Resampling.BICUBIC
    scaled_image = image.resize((target_width, target_height), resampling)

    left_crop = (target_width - monitor.width) // 2
    top_crop = (target_height - monitor.height) // 2
    right_crop = left_crop + monitor.width
    bottom_crop = top_crop + monitor.height

    return scaled_image.crop((left_crop, top_crop, right_crop, bottom_crop))


def __fit_image_to_screen_contain(image: Image.Image, monitor: MMMonitor, background_color: str) -> Image.Image:
    """
    Fit the image within monitor bounds while preserving aspect ratio,
    centering it on a background of specified color.

    The function calculates the largest size that fits into the
    monitor rectangle without cropping the image.  The resized
    image is then centered and padded with ``background_color``.

    :param image: Source image to be scaled.
    :param monitor: Monitor object providing width and height.
    :param background_color: Color used for padding areas.
    :return: New image sized to fit within the monitor, centered.

    """
    img_aspect = image.width / image.height
    screen_aspect = monitor.width / monitor.height

    if img_aspect < screen_aspect:
        target_width = int(monitor.height * img_aspect)
        target_height = monitor.height
    elif img_aspect > screen_aspect:
        target_height = int(monitor.width / img_aspect)
        target_width = monitor.width
    else:
        target_width = monitor.width
        target_height = monitor.height

    resampling = Image.Resampling.LANCZOS if target_width > image.width else Image.Resampling.BICUBIC
    scaled_image = image.resize((target_width, target_height), resampling)

    return __fit_image_to_screen_centered(scaled_image, monitor, background_color)


def render_image_set(image_set: MMImageSet,
                     output_path: Path,
                     layout: MMDesktopLayout,
                     fit_mode: MMFitMode,
                     background_color: str,
                     bake_screen_icc: bool,
                     compression_quality: int):
    """
    Render a composite image from an image set based on a desktop layout, applying color profile baking
    and fitting rules for each monitor. The function creates a base canvas sized to the total area of
    the layout, then iterates over each monitor to place its corresponding image. Images are converted
    to the target mode and optionally baked with the monitor’s ICC profile or standard sRGB.
    The resulting composite is saved to the specified path using the chosen compression quality.

    :param image_set: A collection mapping device identifiers to image file paths.
    :param output_path: Destination file for the rendered image.
    :param layout: Layout definition containing monitor geometry and positioning information.
    :param fit_mode: Strategy used when an image does not match a monitor’s resolution.
    :param background_color: Color value applied as background during fitting operations.
    :param bake_screen_icc: Flag indicating whether to apply each monitor’s ICC profile.
    :param compression_quality: JPEG quality factor (1–100) for the output image.

    :return: None. The function writes the rendered image directly to disk.
    """
    base_image = Image.new(TARGET_IMAGE_MODE, (layout.total_width, layout.total_height), color=background_color)

    for monitor in layout.monitors:
        image_path = image_set.images.get(monitor.device_id, None)
        if not image_path:
            # No image defined for this monitor.
            continue

        image = Image.open(image_set.images[monitor.device_id])

        if image.mode != TARGET_IMAGE_MODE:
            image = image.convert(TARGET_IMAGE_MODE)

        # If bake_icc is true, we need to bake for the target monitor, else we can just convert to sRGB.
        if bake_screen_icc and monitor.cms_profile:
            __bake_color_profile(image, monitor.cms_profile)
        else:
            __bake_color_profile(image, STANDARD_SRGB_PROFILE)

        img_x_pos = int(monitor.x_pos - layout.min_x)
        img_y_pos = int(monitor.y_pos - layout.min_y)

        if not (image.width == monitor.width and image.height == monitor.height):
            match fit_mode:
                case MMFitMode.CENTERED:
                    image = __fit_image_to_screen_centered(image, monitor, background_color)
                case MMFitMode.COVER:
                    image = __fit_image_to_screen_cover(image, monitor)
                case MMFitMode.CONTAIN:
                    image = __fit_image_to_screen_contain(image, monitor, background_color)

        base_image.paste(image, (img_x_pos, img_y_pos))

    # If we bake the monitor ICC's we should NOT embed the profile.
    embed_icc = None if bake_screen_icc else STANDARD_SRGB_PROFILE.tobytes()
    base_image.save(output_path, icc_profile=embed_icc, quality=compression_quality)
