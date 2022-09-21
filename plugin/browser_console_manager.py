
from selenium.webdriver.remote.webdriver import WebDriver
from datetime import datetime


def capture_output(driver: WebDriver):
    logs = _capture_output(driver)
    return _format_outputs(logs)


def _capture_output(driver: WebDriver):
    return driver.get_log('browser')


def _format_outputs(logs: list) -> str:
    output = ''
    for item in logs:
        i_time = datetime.fromtimestamp(item.get('timestamp', 1662995103213)/1000).strftime('%Y-%m-%d %H:%M:%S')
        i_source = item.get('source')
        i_level = item.get('level')
        i_message = item.get('message')
        output += "{} {} {} {}\n".format(i_time, i_level, i_source, i_message)

    return output
