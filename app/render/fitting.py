from PIL import Image

from app.config.constants import TARGET_IMAGE_MODE
from app.config.model import MMFitMode, MMMonitor


def __fit_image_to_screen_centered(image: Image.Image, monitor: MMMonitor, background_color: str) -> Image.Image:
    """
    Place an image onto a monitor-sized canvas, centering it without scaling and filling the
    remaining area with the background color.

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


def __apply_fit_mode(image: Image.Image, monitor: MMMonitor, fit_mode: MMFitMode, background_color: str) -> Image.Image:
    """
    Resizes and adjusts an image to fit a specified monitor display while applying the requested fitting mode.

    Adjusts the dimensions of the provided image to match or conform to the given monitor's resolution,
    applying either centered cropping, cover (stretching), or contain (scaling with padding) based on
    the specified `fit_mode`. The background color is used for padding when necessary.

    :param Image.Image image: Input PIL Image object to be adjusted for display.
    :param MMMonitor monitor: Monitor object defining the target resolution and dimensions.
    :param MMFitMode fit_mode: Enumeration value specifying how the image should be fitted.
    :param str background_color: Hexadecimal color code (e.g., ``"#RRGGBB"``) used for padding.
    :return: Resized and adjusted PIL Image object that fits the specified monitor dimensions according to
        the provided fitting strategy.

    """
    if image.width == monitor.width and image.height == monitor.height:
        # image already fits monitor perfectly.
        return image

    match fit_mode:
        case MMFitMode.CENTERED:
            return __fit_image_to_screen_centered(image, monitor, background_color)
        case MMFitMode.COVER:
            return __fit_image_to_screen_cover(image, monitor)
        case MMFitMode.CONTAIN:
            return __fit_image_to_screen_contain(image, monitor, background_color)
