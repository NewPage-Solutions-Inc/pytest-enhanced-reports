import logging
from typing import Any

import dotenv
import threading

from _pytest.config import argparsing
from _pytest.fixtures import FixtureRequest
from allure_pytest_bdd.pytest_bdd_listener import PytestBDDListener
from pytest import fixture
import pytest
from pytest_bdd.parser import Feature, Scenario

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains

import wrapt
from selenium.webdriver.support.event_firing_webdriver import EventFiringWebDriver

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
import options

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


@fixture(scope="session", autouse=True)
def screenshotting_driver(report_options, other_configs):
    def _enhanced_driver_getter(driver: WebDriver):
        # Event listener is needed only if the screenshot level is greater than 'error-only'
        if report_options['screenshot_level'] != 'all':
            return driver

        # check if the directory to write screenshots exists
        common_utils._mkdir(report_options["screenshot_dir"])
        return EventFiringWebDriver(driver, WebDriverEventListener(report_options, other_configs))
    return _enhanced_driver_getter


@fixture(scope="session", autouse=True)
def create_wrappers(report_options):
    if report_options['screenshot_level'] != 'all':
        return

    @wrapt.patch_function_wrapper(ActionChains, 'perform')
    def wrap_action_chains_perform_method(wrapped, instance, args, kwargs):
        # here, wrapped is the original perform method in ActionChains
        # instance is `self` (it is not the case for classmethods though),
        # args and kwargs are a tuple and a dict respectively.

        wrapped(*args, **kwargs)  # note it is already bound to the instance

        allure_screenshot._take_screenshot("After performing selenium action chain", report_options, instance._driver)


@fixture(scope="session")
def report_options(request: FixtureRequest) -> dict[str, Any]:
    return options.get_all_values(request)


@pytest.fixture
def screen_recorder(scenario_name, report_options: dict[str, Any]):
    obj = ScreenRecorder()
    obj.video_store = report_options["video_dir"]
    obj.directory = scenario_name

    common_utils._mkdir(obj.video_store)
    yield obj


@pytest.fixture
def video_capture_thread(screen_recorder, selenium):
    recorder_thread = threading.Thread(target=screen_recorder.start_capturing, name='Recorder', args=[selenium])
    yield recorder_thread, screen_recorder


@pytest.fixture(autouse=True)
def scenario_name(request: FixtureRequest) -> str:
    return request.node.nodeid.split('/')[-1].replace("::", " - ")


@pytest.fixture(scope="session", autouse=True)
def cleanup(request: FixtureRequest):
    """Cleanup a testing directory once we are finished."""
    try:
        report_options = request.getfixturevalue('report_options')

        def remove_test_dir():
            if not report_options['keep_videos']:
                common_utils._clean_image_repository(report_options['video_dir'])

            if not report_options['keep_screenshots']:
                common_utils._clean_image_repository(report_options['screenshot_dir'])
            else:
                common_utils._clean_temp_images(report_options['screenshot_dir'])

        request.addfinalizer(remove_test_dir)
    except Exception as error:
        logger.error(f"Error occurred while cleaning up: {error}")


@pytest.fixture(scope="session", autouse=True)
def update_test_results_for_scenario_outline():
    AllureLifecycle.write_test_case = _custom_write_test_case


def pytest_addoption(parser: argparsing.Parser):
    group = parser.getgroup("enhanced-report")
    options.init(group)


def pytest_bdd_before_scenario(request: FixtureRequest, feature: Feature, scenario: Scenario):
    report_options = request.getfixturevalue('report_options')
    if report_options['video_recording']:
        obj_recorder_thread, obj_recorder = request.getfixturevalue('video_capture_thread')
        logging.info("TEST EXECUTION VIDEO RECORDING")
        obj_recorder_thread.start()


def pytest_bdd_step_validation_error(request, feature, scenario, step, step_func):
    report_options = request.getfixturevalue('report_options')

    if report_options['screenshot_level'] == 'none':
        return

    driver = request.getfixturevalue('selenium')
    allure_screenshot._take_screenshot("Step failed", report_options, driver)


def pytest_bdd_step_error(request, feature, scenario, step, step_func):
    driver = request.getfixturevalue('selenium')

    report_options = request.getfixturevalue('report_options')
    if report_options['screenshot_level'] != 'none':
        allure_screenshot._take_screenshot("Step failed", report_options, driver)

    # capture browser's outputs on failure
    capture_log_on_failure = request.config.getoption('capture_log_on_failure')
    if capture_log_on_failure:
        logs = browser_console_manager.capture_output(driver)
        allure.attach(bytes(logs, 'utf-8'), 'Browser Outputs', AttachmentType.TEXT)


def pytest_bdd_after_scenario(request, feature, scenario):
    report_options = request.getfixturevalue('report_options')
    scenario_name = request.getfixturevalue('scenario_name')
    if report_options['video_recording']:
        obj_recorder_thread, obj_recorder = request.getfixturevalue('video_capture_thread')
        obj_recorder.stop_recording_and_stitch_video(report_options, obj_recorder_thread, scenario_name, scenario_name)


def _custom_write_test_case(self, uuid=None):
    """Allure has an open bug (https://github.com/allure-framework/allure-python/issues/636) which prevents the
    inclusion of tests with scenario outlines in allure report. There is no fix available yet so we manually remove the
    params which are equals to '_pytest_bdd_example', this param if included in test results, causes errors in report
    generation hence report doesn't include scenario outlines"""
    test_result = self._pop_item(uuid=uuid, item_type=TestResult)
    if test_result:
        if test_result.parameters:
            adj_parameters = []
            for param in test_result.parameters:
                if param.name != '_pytest_bdd_example':
                    # do not include parameters with "_pytest_bdd_example"
                    adj_parameters.append(param)
            test_result.parameters = adj_parameters

        plugin_manager.hook.report_result(result=test_result)


@fixture(scope="session", autouse=True)
def wrapper_for_unexecuted_steps():
    """ When a bdd step fails, test execution is stopped hence next steps are not executed,
    allure report doesn't include the steps that were not executed due to a failed step before them
    To overcome this issue we are intercepting the PytestBDDListener._scenario_finalizer method to add the
    non executed steps to test results """
    @wrapt.patch_function_wrapper(PytestBDDListener, '_scenario_finalizer')
    def wrap_scenario_finalizer(wrapped, instance, args, kwargs):
        # here, wrapped is the original perform method in PytestBDDListener
        # instance is `self` (it is not the case for classmethods though),
        # args and kwargs are a tuple and a dict respectively.

        wrapped(*args, **kwargs)  # note it is already bound to the instance

        test_result = instance.lifecycle._get_item(uuid=instance.lifecycle._last_item_uuid(item_type=TestResult),
                                     item_type=TestResult)
        if len(args[0].steps) > len(test_result.steps):
            for i in range(len(test_result.steps), len(args[0].steps)):
                test_result.steps.append(
                    TestStepResult(name=f'{args[0].steps[i].keyword} {args[0].steps[i].name}', status='skipped')
                )
