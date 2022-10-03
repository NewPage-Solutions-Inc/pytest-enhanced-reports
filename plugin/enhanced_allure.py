import logging
import dotenv
import threading

from allure_pytest_bdd.pytest_bdd_listener import PytestBDDListener
from pytest import fixture
import pytest

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains

import wrapt
from selenium.webdriver.support.event_firing_webdriver import (
    EventFiringWebDriver,
)

from webdriver_event_listener import WebDriverEventListener
import allure_screenshot
from allure_video_recording import ScreenRecorder

from allure_commons.lifecycle import AllureLifecycle
from allure_commons.model2 import TestResult
from allure_commons import plugin_manager
from allure_commons.model2 import TestStepResult
import allure
from allure_commons.types import AttachmentType
import browser_console_manager
import common_utils

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


@fixture(scope="session", autouse=True)
def screenshotting_driver(report_screenshot_options, other_configs):
    def _enhanced_driver_getter(driver: WebDriver):
        # Event listener is needed only if the screenshot level is greater than 'error-only'
        if report_screenshot_options["screenshot_level"] != "all":
            return driver

        # check if the directory to write screenshots exists
        common_utils._mkdir(report_screenshot_options["screenshot_dir"])
        return EventFiringWebDriver(
            driver,
            WebDriverEventListener(report_screenshot_options, other_configs),
        )

    return _enhanced_driver_getter


@fixture(scope="session", autouse=True)
def create_wrappers(report_screenshot_options):
    if report_screenshot_options["screenshot_level"] != "all":
        return

    @wrapt.patch_function_wrapper(ActionChains, "perform")
    def wrap_action_chains_perform_method(wrapped, instance, args, kwargs):
        # here, wrapped is the original perform method in ActionChains
        # instance is `self` (it is not the case for classmethods though),
        # args and kwargs are a tuple and a dict respectively.

        wrapped(*args, **kwargs)  # note it is already bound to the instance

        allure_screenshot._take_screenshot(
            "After performing selenium action chain",
            report_screenshot_options,
            instance._driver,
        )


@fixture(scope="session")
def report_screenshot_options(request) -> dict:
    cmd_line_plugin_options: dict = {
        "screenshot_level": request.config.getoption(
            "report_screenshot_level"
        ),
        "resize_percent": request.config.getoption(
            "report_screenshot_resize_percent"
        ),
        "resize_width": request.config.getoption("report_screenshot_width"),
        "resize_height": request.config.getoption("report_screenshot_height"),
        "screenshot_dir": request.config.getoption("report_screenshot_dir"),
        "keep_screenshots": request.config.getoption(
            "report_keep_screenshots"
        ),
    }

    env_plugin_options: dict = {
        "screenshot_level": common_utils._get_env_var(
            "REPORT_SCREENSHOT_LEVEL", default_value="all"
        ),
        "resize_percent": common_utils._get_env_var(
            "REPORT_SCREENSHOT_RESIZE_PERCENT"
        ),
        "resize_width": common_utils._get_env_var("REPORT_SCREENSHOT_WIDTH"),
        "resize_height": common_utils._get_env_var("REPORT_SCREENSHOT_HEIGHT"),
        "screenshot_dir": common_utils._get_env_var(
            "REPORT_SCREENSHOT_DIR", default_value="screenshots/"
        ),
        "keep_screenshots": common_utils._get_env_var(
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
        keep_screenshots = (
            str(env_plugin_options["keep_screenshots"]).lower() == "true"
        )

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
    elif (
        env_plugin_options["resize_width"]
        and env_plugin_options["resize_height"]
    ):
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


@pytest.fixture
def screen_recorder(report_video_recording_options):
    obj = ScreenRecorder()
    obj.video_store = report_video_recording_options["video_dir"]
    if "scenario_name" in report_video_recording_options:
        obj.directory = report_video_recording_options["scenario_name"]

    common_utils._mkdir(obj.video_store)
    yield obj


@pytest.fixture
def video_capture_thread(screen_recorder, selenium):
    recorder_thread = threading.Thread(
        target=screen_recorder.start_capturing,
        name="Recorder",
        args=[selenium],
    )
    yield recorder_thread, screen_recorder


@fixture(scope="session")
def report_video_recording_options(request) -> dict:
    cmd_line_plugin_options: dict = {
        "video_recording": request.config.getoption("report_video_recording"),
        "video_dir": request.config.getoption("report_video_dir"),
        "video_width": request.config.getoption("report_video_width"),
        "video_height": request.config.getoption("report_video_height"),
        "video_frame_rate": request.config.getoption(
            "report_video_frame_rate"
        ),
        "video_resize_percentage": request.config.getoption(
            "report_video_resize_percentage"
        ),
        "keep_videos": request.config.getoption("report_keep_videos"),
    }

    env_plugin_options: dict = {
        "video_recording": common_utils._get_env_var(
            "REPORT_VIDEO_RECORDING", default_value=False
        ),
        "video_dir": common_utils._get_env_var(
            "REPORT_VIDEO_DIR", default_value="videos"
        ),
        "video_width": common_utils._get_env_var("REPORT_VIDEO_WIDTH"),
        "video_height": common_utils._get_env_var("REPORT_VIDEO_HEIGHT"),
        "video_frame_rate": common_utils._get_env_var(
            "REPORT_VIDEO_FRAME_RATE", default_value=5
        ),
        "video_resize_percentage": common_utils._get_env_var(
            "REPORT_VIDEO_RESIZE_PERCENTAGE", default_value=30
        ),
        "keep_videos": common_utils._get_env_var(
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
        video_recording = (
            str(env_plugin_options["video_recording"]).lower() == "true"
        )

    if cmd_line_plugin_options["video_dir"]:
        video_dir = cmd_line_plugin_options["video_dir"]
    else:
        video_dir = env_plugin_options["video_dir"]

    if cmd_line_plugin_options["video_frame_rate"]:
        video_frame_rate = cmd_line_plugin_options["video_frame_rate"]
    elif env_plugin_options["video_frame_rate"]:
        video_frame_rate = env_plugin_options["video_frame_rate"]

    if cmd_line_plugin_options["keep_videos"]:
        keep_videos = (
            str(cmd_line_plugin_options["keep_videos"]).lower() == "true"
        )
    else:
        keep_videos = str(env_plugin_options["keep_videos"]).lower() == "true"

    if (
        cmd_line_plugin_options["video_width"]
        and cmd_line_plugin_options["video_height"]
    ):
        video_width = cmd_line_plugin_options["video_width"]
        video_height = cmd_line_plugin_options["video_height"]
    elif (
        env_plugin_options["video_width"]
        and env_plugin_options["video_height"]
    ):
        video_width = env_plugin_options["video_width"]
        video_height = env_plugin_options["video_height"]
    else:
        if cmd_line_plugin_options["video_resize_percentage"]:
            video_resize_percentage = cmd_line_plugin_options[
                "video_resize_percentage"
            ]
        elif env_plugin_options["video_resize_percentage"]:
            video_resize_percentage = env_plugin_options[
                "video_resize_percentage"
            ]

    return {
        "video_recording": video_recording,
        "video_dir": video_dir,
        "video_height": video_height,
        "video_width": video_width,
        "video_frame_rate": video_frame_rate,
        "video_resize_percentage": video_resize_percentage,
        "keep_videos": keep_videos,
    }


@pytest.fixture
def update_test_name_in_options(
    report_screenshot_options, report_video_recording_options, request
):
    if report_screenshot_options["screenshot_level"] != "none":
        report_screenshot_options["scenario_name"] = request.node.nodeid.split(
            "/"
        )[-1].replace("::", " - ")
    if report_video_recording_options["video_recording"]:
        report_video_recording_options[
            "scenario_name"
        ] = request.node.nodeid.split("/")[-1].replace("::", " - ")

    return report_screenshot_options, report_video_recording_options


@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    """Cleanup a testing directory once we are finished."""
    try:
        video_options = request.getfixturevalue(
            "report_video_recording_options"
        )
        screenshot_options = request.getfixturevalue(
            "report_screenshot_options"
        )

        def remove_test_dir(video_options_, screenshot_options_):
            if not video_options_["keep_videos"]:
                common_utils._clean_image_repository(
                    video_options_["video_dir"]
                )

            if not screenshot_options_["keep_screenshots"]:
                common_utils._clean_image_repository(
                    screenshot_options_["screenshot_dir"]
                )
            else:
                common_utils._clean_temp_images(
                    screenshot_options_["screenshot_dir"]
                )

        request.addfinalizer(
            lambda: remove_test_dir(video_options, screenshot_options)
        )
    except Exception as error:
        logger.error(f"Error occurred while cleaning up: {error}")


@pytest.fixture(scope="session", autouse=True)
def update_test_results_for_scenario_outline():
    AllureLifecycle.write_test_case = _custom_write_test_case


def pytest_addoption(parser):
    # a percentage by which the screenshot will be resized. valid values - 75, 60, 50, etc
    parser.addoption(
        "--report_screenshot_resize_percent", action="store", default=0
    )

    # the expected width of the resized screenshot used in reports.
    # the actual width of the image used in reports could be different depending on the aspect ratio of the image
    parser.addoption("--report_screenshot_width", action="store", default=0)

    # the expected height of the resized screenshot used in reports.
    # the actual height of the image used in reports could be different depending on the aspect ratio of the image
    parser.addoption("--report_screenshot_height", action="store", default=0)

    # valid values for screenshot level are 'none', 'all', 'error-only'
    parser.addoption("--report_screenshot_level", action="store", default=None)

    # valid values for video recording are 'true', 'false'
    parser.addoption("--report_video_recording", action="store", default=0)

    # expected width of video frame to be recorded
    parser.addoption("--report_video_width", action="store", default=0)

    # expected height of video frame to be recorded
    parser.addoption("--report_video_height", action="store", default=0)

    # expected number of frames per second while recording video.
    # this is applicable when there are enough frames present to be recorded in one second
    parser.addoption("--report_video_frame_rate", action="store", default=0)

    # a percentage by which the video frames will be resized. valid values - 75, 60, 50, etc
    parser.addoption(
        "--report_video_resize_percentage", action="store", default=0
    )

    # path to folder where user wants to preserve screenshots
    parser.addoption("--report_screenshot_dir", action="store", default=0)

    # path to folder where user wants to preserve videos
    parser.addoption("--report_video_dir", action="store", default=0)

    # flag is used to decide whether user wants to preserve screenshots
    parser.addoption("--report_keep_screenshots", action="store", default=0)

    # flag is used to decide whether user wants to preserve videos
    parser.addoption("--report_keep_videos", action="store", default=0)

    # flag is used to decide whether user wants to capture all console output when test is failed
    parser.addoption("--capture_log_on_failure", action="store", default=0)

    # flag is used to decide whether user wants to capture console output on each action
    parser.addoption("--always_capture_log", action="store", default=0)

    # flag is used to decide whether user wants to highlight element and capture screenshot of that element before
    # interacting with this element
    parser.addoption("--highlight_element", action="store", default=False)


def pytest_bdd_before_scenario(request, feature, scenario):
    screenshot_options, video_options = request.getfixturevalue(
        "update_test_name_in_options"
    )
    video_recording = video_options["video_recording"]
    if video_recording:
        obj_recorder_thread, obj_recorder = request.getfixturevalue(
            "video_capture_thread"
        )
        obj_recorder_thread.start()
    logging.info("TEST EXECUTION VIDEO RECORDING: " + str(video_recording))


def pytest_bdd_step_validation_error(
    request, feature, scenario, step, step_func
):
    report_screenshot_options = request.getfixturevalue(
        "report_screenshot_options"
    )

    if report_screenshot_options["screenshot_level"] == "none":
        return

    driver = request.getfixturevalue("selenium")
    allure_screenshot._take_screenshot(
        "Step failed", report_screenshot_options, driver
    )


def pytest_bdd_step_error(request, feature, scenario, step, step_func):
    driver = request.getfixturevalue("selenium")

    report_screenshot_options = request.getfixturevalue(
        "report_screenshot_options"
    )
    if report_screenshot_options["screenshot_level"] != "none":
        allure_screenshot._take_screenshot(
            "Step failed", report_screenshot_options, driver
        )

    # capture browser's outputs on failure
    capture_log_on_failure = request.config.getoption("capture_log_on_failure")
    if capture_log_on_failure:
        logs = browser_console_manager.capture_output(driver)
        allure.attach(
            bytes(logs, "utf-8"), "Browser Outputs", AttachmentType.TEXT
        )


def pytest_bdd_after_scenario(request, feature, scenario):
    video_options = request.getfixturevalue("report_video_recording_options")
    screenshot_options = request.getfixturevalue("report_screenshot_options")
    if video_options["video_recording"]:
        scenario_info = video_options["scenario_name"]
        obj_recorder_thread, obj_recorder = request.getfixturevalue(
            "video_capture_thread"
        )
        obj_recorder.stop_recording_and_stitch_video(
            video_options, obj_recorder_thread, scenario_info, scenario.name
        )


def _custom_write_test_case(self, uuid=None):
    """Allure has an open bug (https://github.com/allure-framework/allure-python/issues/636) which prevents the
    inclusion of tests with scenario outlines in allure report. There is no fix available yet so we manually remove the
    params which are equals to '_pytest_bdd_example', this param if included in test results, causes errors in report
    generation hence report doesnt include scenario outlines"""
    test_result = self._pop_item(uuid=uuid, item_type=TestResult)
    if test_result:
        if test_result.parameters:
            adj_parameters = []
            for param in test_result.parameters:
                if param.name != "_pytest_bdd_example":
                    # do not include parameters with "_pytest_bdd_example"
                    adj_parameters.append(param)
            test_result.parameters = adj_parameters

        plugin_manager.hook.report_result(result=test_result)


@fixture(scope="session", autouse=True)
def wrapper_for_unexecuted_steps():
    """When a bdd step fails, test execution is stopped hence next steps are not executed,
    allure report doesn't include the steps that were not executed due to a failed step before them
    To overcome this issue we are intercepting the PytestBDDListener._scenario_finalizer method to add the
    non executed steps to test results"""

    @wrapt.patch_function_wrapper(PytestBDDListener, "_scenario_finalizer")
    def wrap_scenario_finalizer(wrapped, instance, args, kwargs):
        # here, wrapped is the original perform method in PytestBDDListener
        # instance is `self` (it is not the case for classmethods though),
        # args and kwargs are a tuple and a dict respectively.

        wrapped(*args, **kwargs)  # note it is already bound to the instance

        test_result = instance.lifecycle._get_item(
            uuid=instance.lifecycle._last_item_uuid(item_type=TestResult),
            item_type=TestResult,
        )
        if len(args[0].steps) > len(test_result.steps):
            for i in range(len(test_result.steps), len(args[0].steps)):
                test_result.steps.append(
                    TestStepResult(
                        name=f"{args[0].steps[i].keyword} {args[0].steps[i].name}",
                        status="skipped",
                    )
                )
