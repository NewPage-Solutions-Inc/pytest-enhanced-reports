import logging
import dotenv
from pytest import fixture
import common_utils

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


@fixture(scope="session")
def report_screenshot_options(request) -> dict:
    cmd_line_plugin_options: dict = {
        "screenshot_level": request.config.getoption("report_screenshot_level"),
        "resize_percent": request.config.getoption("report_screenshot_resize_percent"),
        "resize_width": request.config.getoption("report_screenshot_width"),
        "resize_height": request.config.getoption("report_screenshot_height"),
        "screenshot_dir": request.config.getoption("report_screenshot_dir"),
        "keep_screenshots": request.config.getoption("report_keep_screenshots"),
    }

    env_plugin_options: dict = {
        "screenshot_level": common_utils.get_env_var(
            "REPORT_SCREENSHOT_LEVEL", default_value="all"
        ),
        "resize_percent": common_utils.get_env_var("REPORT_SCREENSHOT_RESIZE_PERCENT"),
        "resize_width": common_utils.get_env_var("REPORT_SCREENSHOT_WIDTH"),
        "resize_height": common_utils.get_env_var("REPORT_SCREENSHOT_HEIGHT"),
        "screenshot_dir": common_utils.get_env_var(
            "REPORT_SCREENSHOT_DIR", default_value="screenshots/"
        ),
        "keep_screenshots": common_utils.get_env_var(
            "REPORT_KEEP_SCREENSHOTS", default_value=False
        ),
    }

    resize_percent = None
    resize_width = None
    resize_height = None

    screenshot_level = None
    screenshot_dir = None
    keep_screenshots = None

    if cmd_line_plugin_options["screenshot_level"]:
        screenshot_level = cmd_line_plugin_options["screenshot_level"]
    else:
        screenshot_level = env_plugin_options["screenshot_level"]

    if cmd_line_plugin_options["screenshot_dir"]:
        screenshot_dir = cmd_line_plugin_options["screenshot_dir"]
    else:
        screenshot_dir = env_plugin_options["screenshot_dir"]

    if cmd_line_plugin_options["keep_screenshots"]:
        keep_screenshots = (
            str(cmd_line_plugin_options["keep_screenshots"]).lower() == "true"
        )
    else:
        keep_screenshots = str(env_plugin_options["keep_screenshots"]).lower() == "true"

    """
    Order of precedence for resize config:
    1. Specific resolution
        1.1 - From command line options
        1.2 - From environment variables
    2. Resize percentage
        2.1 - From command line option
        2.2 - From environment variable
    3. Default value (defined in the resize method)
    """
    if (
        cmd_line_plugin_options["resize_width"]
        and cmd_line_plugin_options["resize_height"]
    ):
        resize_width = cmd_line_plugin_options["resize_width"]
        resize_height = cmd_line_plugin_options["resize_height"]
    elif env_plugin_options["resize_width"] and env_plugin_options["resize_height"]:
        resize_width = env_plugin_options["resize_width"]
        resize_height = env_plugin_options["resize_height"]
    else:
        if cmd_line_plugin_options["resize_percent"]:
            resize_percent = cmd_line_plugin_options["resize_percent"]
        elif env_plugin_options["resize_percent"]:
            resize_percent = env_plugin_options["resize_percent"]

    return {
        "screenshot_level": screenshot_level,
        "screenshot_dir": screenshot_dir,
        "resize_percent": resize_percent,
        "resize_width": resize_width,
        "resize_height": resize_height,
        "keep_screenshots": keep_screenshots,
    }


@fixture(scope="session")
def other_configs(request) -> dict:
    return {
        "always_capture_log": True
        if request.config.getoption("always_capture_log") == "True"
        else False,
        "highlight_element": True
        if request.config.getoption("highlight_element") == "True"
        else False,
    }


@fixture(scope="session")
def report_video_recording_options(request) -> dict:
    cmd_line_plugin_options: dict = {
        "video_recording": request.config.getoption("report_video_recording"),
        "video_dir": request.config.getoption("report_video_dir"),
        "video_width": request.config.getoption("report_video_width"),
        "video_height": request.config.getoption("report_video_height"),
        "video_frame_rate": request.config.getoption("report_video_frame_rate"),
        "video_resize_percentage": request.config.getoption(
            "report_video_resize_percentage"
        ),
        "keep_videos": request.config.getoption("report_keep_videos"),
    }

    env_plugin_options: dict = {
        "video_recording": common_utils.get_env_var(
            "REPORT_VIDEO_RECORDING", default_value=False
        ),
        "video_dir": common_utils.get_env_var(
            "REPORT_VIDEO_DIR", default_value="videos"
        ),
        "video_width": common_utils.get_env_var("REPORT_VIDEO_WIDTH"),
        "video_height": common_utils.get_env_var("REPORT_VIDEO_HEIGHT"),
        "video_frame_rate": common_utils.get_env_var(
            "REPORT_VIDEO_FRAME_RATE", default_value=5
        ),
        "video_resize_percentage": common_utils.get_env_var(
            "REPORT_VIDEO_RESIZE_PERCENTAGE", default_value=30
        ),
        "keep_videos": common_utils.get_env_var(
            "REPORT_KEEP_VIDEOS", default_value=False
        ),
    }

    video_recording = None
    video_height = None
    video_width = None
    video_frame_rate = None
    video_resize_percentage = None
    video_dir = None
    keep_videos = None

    if cmd_line_plugin_options["video_recording"]:
        video_recording = (
            str(cmd_line_plugin_options["video_recording"]).lower() == "true"
        )
    else:
        video_recording = str(env_plugin_options["video_recording"]).lower() == "true"

    if cmd_line_plugin_options["video_dir"]:
        video_dir = cmd_line_plugin_options["video_dir"]
    else:
        video_dir = env_plugin_options["video_dir"]

    if cmd_line_plugin_options["video_frame_rate"]:
        video_frame_rate = cmd_line_plugin_options["video_frame_rate"]
    elif env_plugin_options["video_frame_rate"]:
        video_frame_rate = env_plugin_options["video_frame_rate"]

    if cmd_line_plugin_options["keep_videos"]:
        keep_videos = str(cmd_line_plugin_options["keep_videos"]).lower() == "true"
    else:
        keep_videos = str(env_plugin_options["keep_videos"]).lower() == "true"

    if (
        cmd_line_plugin_options["video_width"]
        and cmd_line_plugin_options["video_height"]
    ):
        video_width = cmd_line_plugin_options["video_width"]
        video_height = cmd_line_plugin_options["video_height"]
    elif env_plugin_options["video_width"] and env_plugin_options["video_height"]:
        video_width = env_plugin_options["video_width"]
        video_height = env_plugin_options["video_height"]
    else:
        if cmd_line_plugin_options["video_resize_percentage"]:
            video_resize_percentage = cmd_line_plugin_options["video_resize_percentage"]
        elif env_plugin_options["video_resize_percentage"]:
            video_resize_percentage = env_plugin_options["video_resize_percentage"]

    return {
        "video_recording": video_recording,
        "video_dir": video_dir,
        "video_height": video_height,
        "video_width": video_width,
        "video_frame_rate": video_frame_rate,
        "video_resize_percentage": video_resize_percentage,
        "keep_videos": keep_videos,
    }
