from typing import Mapping, Any, Union

import common_utils
from _pytest.config import argparsing
from _pytest.fixtures import FixtureRequest

import logging
import json

logger = logging.getLogger(__name__)


__default_action = "store"
__default_prefix = "report_"

__arg_values: Mapping[str, Any] = {}

with open("data/parameters.json", "r") as f:
    __args: Mapping[str, Mapping[str, Any]] = json.load(f)

# __args: Mapping[str, Mapping[str, Any]] = {
#     "capture_browser_console_log": {
#         "default_value": "on_failure",
#         "doc": "Specifies when to capture info from the browser console log. Valid values are 'on_failure', "
#         "'always' and 'never'. Default is 'on_failure'",
#     },
#     "screenshot_level": {
#         "default_value": "all",
#         "doc": "Specifies when to capture screenshots. Valid values are 'none', 'all', 'error-only'. Default is 'all'",
#     },
#     "screenshot_resize_percent": {
#         "default_value": 40,
#         "doc": "A percentage by which the screenshot will be resized. valid values - 75, 60, 50, etc",
#     },
#     "screenshot_height": {
#         "default_value": 0,
#         "doc": "The expected height of the resized screenshot used in reports. Actual value could be different as it "
#         "needs to fit the aspect ratio",
#     },
#     "screenshot_width": {
#         "default_value": 0,
#         "doc": "The expected width of the resized screenshot used in reports. Actual value could be different as it "
#         "needs to fit the aspect ratio",
#     },
#     "highlight_element": {
#         "default_value": False,
#         "doc": "If set to True, the element being interacted with will be highlighted before taking the screenshot. "
#         "Default is False",
#     },
#     "keep_screenshots": {
#         "default_value": False,
#         "doc": "If set to True, generated screenshot images will not be deleted after the test run. Defaults to False",
#     },
#     "screenshot_dir": {
#         "default_value": None,
#         "doc": "The path to the directory where screenshots will be stored",
#     },
#     "video_recording": {
#         "default_value": False,
#         "doc": "If set to True, a video will be recorded for each test. Default is False",
#     },
#     "keep_videos": {
#         "default_value": False,
#         "doc": "If set to True, generated video files will not be deleted after the test run. Defaults to False",
#     },
#     "video_dir": {
#         "default_value": None,
#         "doc": "The path to the directory where video files will be stored",
#     },
#     "video_resize_percentage": {
#         "default_value": 75,
#         "doc": "A percentage by which the video frames will be resized. valid values - 75, 60, 50, etc",
#     },
#     "video_frame_rate": {
#         "default_value": 30,
#         "doc": "The expected number of frames per second while recording a video. This is applicable only when there "
#         "enough frames were recorded in one second, which is not guaranteed.",
#     },
#     "video_height": {
#         "default_value": 0,
#         "doc": "Expected height of the video. Actual value could be different as it needs to fit the aspect ratio",
#     },
#     "video_width": {
#         "default_value": 0,
#         "doc": "Expected width of the video. Actual value could be different as it needs to fit the aspect ratio",
#     },
# }


def _get_value(request: FixtureRequest, arg_name: str):
    full_arg_name: str = f"{__default_prefix}{arg_name}"
    val_from_env_var = common_utils.get_env_var(
        full_arg_name.upper(), default_value=__args[arg_name]["default_value"]
    )
    return request.config.getoption(full_arg_name, default=val_from_env_var)


def init(parser_or_group: Union[argparsing.Parser, argparsing.OptionGroup]):
    """Adds the command line arguments to the parser"""
    for arg_name, arg_details in __args.items():
        parser_or_group.addoption(
            f"--{__default_prefix}{arg_name}",
            action=arg_details.get("action", __default_action),
            default=arg_details.get("default_value", None),
            help=arg_details.get("doc", "No docstring for this argument"),
        )


def get_all_values(request: FixtureRequest):
    """Returns a dictionary with values for all the options"""
    global __arg_values

    if __arg_values:
        return __arg_values

    logger.info("Getting values for all the options")
    __arg_values = {
        arg_name: _get_value(request, arg_name) for arg_name in __args.keys()
    }
    return __arg_values


def get_value(request: FixtureRequest, arg_name: str):
    """Gets the value for a specified argument.
    Looks for the argument in the following order:
    1. Command line argument
    2. Environment variable
    3. Default value, set by the plugin
    """
    return get_all_values(request)[arg_name]
