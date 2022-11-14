import logging
import os
from typing import Tuple
from PIL import Image

logger = logging.getLogger(__name__)


def get_resized_resolution(width, height, resize_factor) -> Tuple[int, int]:
    new_width = int(width * resize_factor)
    new_height = int(height * resize_factor)
    return new_width, new_height


def mkdir(dir_name):
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)


def delete_dir(dir_path):
    if os.path.isdir(dir_path):
        for f in os.listdir(dir_path):
            if os.path.isdir(os.path.join(dir_path, f)):
                delete_dir(os.path.join(dir_path, f))
            else:
                os.remove(os.path.join(dir_path, f))
        os.rmdir(dir_path)
        logger.info(f"Deleted the dir '{dir_path}'")


def clean_temp_images(img_dir, file_name=None):  # TODO: Test if this removes only the temp images. Doesn't look like it
    # Now clean the images directory or a single file if specified
    if file_name is None:
        if os.path.isdir(img_dir):
            for f in os.listdir(img_dir):
                if f.__contains__("png"):
                    os.remove(os.path.join(img_dir, f))
            logger.info(f"Temporary images cleaned from {img_dir}")
    else:
        os.remove(os.path.join(img_dir, file_name))


def clean_filename(value: str) -> str:
    # remove the undesirable characters
    import re
    regex: str = r"\b\d*[^\W\d_][^\W_]*\b"  # From https://stackoverflow.com/a/58835448/5376299
    return re.sub(regex, "", value, 0, re.MULTILINE)


def fail_silently(func):
    """Decorator that makes sure that any errors/exceptions do not get outside the plugin"""

    def wrapped_func(*args, **kws):
        try:
            return func(*args, **kws)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")

    return wrapped_func


def get_original_resolution(directory, file_name=None):
    """get the original resolution of an image"""
    if not file_name:
        img = Image.open(
            os.path.join(
                directory,
                [f for f in os.listdir(directory) if f.endswith(".png")][0],
            )
        )
    else:
        img = Image.open(os.path.join(directory, file_name))
    return img.width, img.height
