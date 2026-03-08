from io import BytesIO

from PIL import Image
from PIL.ImageCms import ImageCmsProfile, profileToProfile, Intent

from app.config.constants import STANDARD_SRGB_PROFILE, TARGET_IMAGE_MODE


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
