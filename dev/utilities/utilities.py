import base64
import io
import os

import pytest
from PIL import Image
from io import BytesIO
from dev import settings


# remove all file IO (not possible)
# 1000 x 0.3 = 330
# 800 x
# write a fixture or hooks for getting command line arguments like screenshot width and height
# %age mainly
# %age > width, height > default values
# add commands lines arguments for %age and both height and width


def image_to_byte_array(image: Image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format=image.format)
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr


def takes_screenshot_for_allure_not(driver):
    imagesize =100
    if imagesize == 100:
        # open the image in memory
        img = Image.open(BytesIO(base64.b64decode(driver.get_screenshot_as_base64())))
        img.thumbnail((int(settings.IMAGE_HEIGHT), int(settings.IMAGE_WIDTH)))
        img.save("reports/screenshot.png")
        with open("reports/screenshot.png", 'rb') as image:
            file = image.read()
            byte_array = bytearray(file)
        return byte_array

    else:
        # open the image in memory
        img = Image.open(BytesIO(base64.b64decode(driver.get_screenshot_as_base64())))
        actual_size = img.size
        print('---size of image is')
        print(actual_size)
        img.save("reports/screenshot.png")
        with open("reports/screenshot.png", 'rb') as image:
            file = image.read()
            byte_array = bytearray(file)
        return byte_array


def take_screenshot_for_allure(driver):
    # open the image in memory
    img = Image.open(BytesIO(base64.b64decode(driver.get_screenshot_as_base64())))
    img.thumbnail((int(settings.IMAGE_HEIGHT), int(settings.IMAGE_WIDTH)))
    img.save("reports/screenshot.png")
    with open("reports/screenshot.png", 'rb') as image:
        file = image.read()
        byte_array = bytearray(file)
    return byte_array


def take_screenshot_for_allure_worked(driver):
    # open the image in memory
    img = Image.open(BytesIO(base64.b64decode(driver.get_screenshot_as_base64())))
    img.thumbnail((int(settings.IMAGE_HEIGHT), int(settings.IMAGE_WIDTH)))
    img.save("reports/screenshot.png")
    with open("reports/screenshot.png", 'rb') as image:
        file = image.read()
        byte_array = bytearray(file)
    return byte_array


def take_screenshot_for_allure_old(driver):
    size_720 = (800, 600)
    name = 'screenshot_after_navigating.png'
    driver.save_screenshot("reports/" + name)
    i = Image.open("reports/" + name)
    fn, fext = os.path.splitext("reports/" + name)
    i.thumbnail(size_720)
    i.save('{}{}'.format(fn, fext))
    with open("reports/screenshot_after_navigating.png", 'rb') as image:
        file = image.read()
        byte_array = bytearray(file)
    return byte_array


