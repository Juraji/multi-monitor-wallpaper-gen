from pathlib import Path

from PIL import Image

from app.config import MMFitMode, MMDesktopLayout, MMImageSet, STANDARD_SRGB_PROFILE, TARGET_IMAGE_MODE
from .fitting import __apply_fit_mode
from .icc import __bake_color_profile


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

        # Apply fit mode.
        image = __apply_fit_mode(image, monitor, fit_mode, background_color)

        img_x_pos = int(monitor.x_pos - layout.min_x)
        img_y_pos = int(monitor.y_pos - layout.min_y)
        base_image.paste(image, (img_x_pos, img_y_pos))

    # If we bake the monitor ICC's we should NOT embed the profile.
    embed_icc = None if bake_screen_icc else STANDARD_SRGB_PROFILE.tobytes()
    base_image.save(output_path, icc_profile=embed_icc, quality=compression_quality)
