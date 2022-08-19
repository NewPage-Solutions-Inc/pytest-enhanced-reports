import logging
import os
import dotenv

from typing import Tuple

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


def _get_env_var(env_var_name, default_value=None):
    return os.getenv(env_var_name, default_value)


def _get_resized_resolution(width, height, resize_factor) -> Tuple[int, int]:
    new_width = int(width * resize_factor)
    new_height = int(height * resize_factor)
    return new_width, new_height


def _mkdir(dir_name):
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)


def _clean_image_repository(img_dir):
    # Now clean the images directory
    if os.path.isdir(img_dir):
        for f in os.listdir(img_dir):
            if os.path.isdir(os.path.join(img_dir, f)):
                _clean_image_repository(os.path.join(img_dir, f))
            else:
                os.remove(os.path.join(img_dir, f))
        os.rmdir(img_dir)
        logger.info(f"IMAGE REPOSOTORY CLEANED. {img_dir} FOLDER DELETED.")


def _clean_temp_images(img_dir, file_name=None):
    # Now clean the images directory or a single file if specified
    if file_name is None:
        if os.path.isdir(img_dir):
            for f in os.listdir(img_dir):
                if f.__contains__('png'):
                    os.remove(os.path.join(img_dir, f))
            logger.info(f"Temporary images cleaned from {img_dir}")
    else:
        os.remove(os.path.join(img_dir, file_name))

