import logging
import os
import re
from typing import Tuple
from PIL import Image

logger = logging.getLogger(__name__)
logger.info("Loaded " + __file__)


def get_resized_resolution(width, height, resize_factor) -> Tuple[int, int]:
    new_width = int(width * resize_factor)
    new_height = int(height * resize_factor)
    return new_width, new_height


def mkdir(dir_name):
    os.makedirs(dir_name, exist_ok=True)


def delete_dir(dir_path):
    if os.path.isdir(dir_path):
        for f in os.listdir(dir_path):
            if os.path.isdir(os.path.join(dir_path, f)):
                delete_dir(os.path.join(dir_path, f))
            else:
                os.remove(os.path.join(dir_path, f))
        os.rmdir(dir_path)
        logger.debug(f"Deleted the dir '{dir_path}'")


def delete_files(img_dir, file_name=None, extension="png"):
    if file_name:
        os.remove(os.path.join(img_dir, file_name))
        return

    if not os.path.isdir(img_dir):
        logger.warning(f"Directory '{img_dir}' does not exist")
        return

    for f in os.listdir(img_dir):
        if f.endswith(extension):
            os.remove(os.path.join(img_dir, f))
    logger.debug(f"Files with extension {extension} deleted from {img_dir}")


def clean_filename(value: str) -> str:
    # remove the undesirable characters
    return re.sub(r"\W", "_", value)


def fail_silently(func):
    """Decorator that makes sure that any errors/exceptions do not get outside the plugin"""

    def wrapped_func(*args, **kws):
        try:
            return func(*args, **kws)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")

    return wrapped_func


def get_image_resolution(directory, file_name=None):
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
