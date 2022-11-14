
# Enhanced test report

---
A pytest plugin to add screenshots, videos and JS logs to test reports (similar to Cypress).

## Support

### Python
* `>= 3.7`

### Browsers
* **Fully supported** - Chromium based browsers - Chrome, Edge, Brave, Opera, Vivaldi, etc
* **Planned in the future** - Firefox, Safari

### Reporting
* **Fully supported** - [allure-pytest-bdd](https://pypi.org/project/allure-pytest-bdd/)
* **Planned in the future** - [pytest-html](https://pypi.org/project/pytest-html/), [pytest-testrail-client](https://pypi.org/project/pytest-testrail-client/)


## Installation
Until the plugin is published on PyPi, it needs to be installed/updated from source.
```bash
pip install -U PATH_TO_THE_PLUGIN_SOURCE_DIR
```

## Usage

### Setup
The plugin needs a code change to be able to capture data from the webdriver instance. Usually, this is just a few lines added to the webdriver initialization logic.

#### Before plugin integration
```python
@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()
```

#### After plugin integration
```python
@pytest.fixture
def driver(screenshotting_driver):  # `screenshotting_driver` is a fixture provided by the plugin
    
    driver = webdriver.Chrome()

    enhanced_driver = None
    try:
        enhanced_driver = screenshotting_driver(driver)
    except Exception as e:
        logger.error(e)

    yield enhanced_driver if enhanced_driver else driver

    driver.quit()
```

### Configuration
The plugin can be configured through command line arguments and/or environment variables. Either option can be used, but if both are provided for any configuration, the command line argument takes precedence over the environment variable.

The following sets of shell commands are equivalent and do the same thing. These examples ignore any configuration for all other plugins/dependencies.
```bash
# Using only command line arguments
pytest --report_screenshot_level="error-only" --report_screenshot_dir="~/tests/screenshots" --report_js_logs_capture="on_failure"
```

```bash
# Using a combination of command line arguments and environment variables
REPORT_SCREENSHOT_DIR="~/tests/screenshots"
pytest --report_screenshot_level="error-only"  --report_js_logs_capture="on_failure"
```

```bash
# Using only environment variables
REPORT_SCREENSHOT_LEVEL="error-only"
REPORT_SCREENSHOT_DIR="~/tests/screenshots"
REPORT_JS_LOGS_CAPTURE="on_failure"
pytest
```

The full list of configuration options are listed below.

### Screenshots
| Configuration Option                    | Expected Value                  | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|-----------------------------------------|---------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **report_screenshot_level**             | 'all' or 'none' or 'error-only' | This flag is used to enable Screenshot capturing. If value is not specified, it will default to **all**.                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **report_screenshot_width**             | int                             | Used to set the width of the screenshot. (the actual width of the image used in reports could be different depending on the aspect ratio of the image)                                                                                                                                                                                                                                                                                                                                                                                     |
| **report_screenshot_height**            | int                             | Used to set the height of the screenshot. (the actual height of the image used in reports could be different depending on the aspect ratio of the image)                                                                                                                                                                                                                                                                                                                                                                                   |
| **report_screenshot_resize_percent**    | int                             | - Used to resize/reduce the height and width of original screenshot to a specific percentage.<br> - If --report_screenshot_width and report_image_resize_height are given along with this flag then this flag will not have any effect.<br>- If --report_screenshot_width and height are not given but this flag is provided then screenshot will be resized to this percentage.<br>- If neither --report_screenshot_width, report_image_resize_height nor report_image_resize_percentage is given then **this flag will default to 30%**. |
| **report_screenshot_dir**               | path to directory               | Used to write the screenshots to attach with allure report. **It will default to `/screenshots`** if not specified by user.                                                                                                                                                                                                                                                                                                                                                                                                                |
| **report_screenshot_keep_files**        | true, false                     | Used to enable user to keep the original screenshots in `screenshots/` or user provided directory                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **report_screenshot_highlight_element** | true, false                     | Used to highlight element and take a screenshot before user's interaction                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |

### Video Recording
| Configuration Option            | Expected Value    | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
|---------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **report_video_recording**      | true, false       | This flag is used to enable video recording. If value is not specified, it will default to **false**.                                                                                                                                                                                                                                                                                                                                                                           |
| **report_video_width**          | int               | Used to set the width of the video frame.                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| **report_video_height**         | int               | Used to set the height of the video frame.                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| **report_video_resize_percent** | int               | - Used to resize/reduce the height and width of original frames to a specific percentage.</br>- If --report_video_width and video_height are given along with this flag then this flag will not have any effect.<br>- If --report_video_width and height are not given but this flag is provided then frame will be resized to this percentage.<br>- If neither --report_video_width, video_height nor video_resize_percentage is given then **this flag will default to 30%**. |
| **report_video_frame_rate**     | int               | Used to set the number of frames per second in the video. **It will default to 5 fps** if not specified by user.                                                                                                                                                                                                                                                                                                                                                                |
| **report_video_dir**            | path to directory | Used to write the videos to attach with allure report. **It will default `/videos`** if not specified by user.                                                                                                                                                                                                                                                                                                                                                                  |
| **report_video_keep_files**     | true, false       | Used to enable user to keep the videos in `videos/` or user provided directory                                                                                                                                                                                                                                                                                                                                                                                                  |

### Browser console outputs
| Configuration Option       | Expected Value                      | Description                                              |
|----------------------------|-------------------------------------|----------------------------------------------------------|
| **report_js_logs_capture** | 'always' or 'never' or 'on_failure' | This flag is used to enable capturing browser's outputs. |


## Contributing
Just the standard fork, branch, commit, test, push, pull request workflow. Including specifics for the sake of documentation.
- Create a fork of [the repo](https://github.com/NewPage-Solutions-Inc/allure-screenshots) and clone the fork
- Install all dependencies from `requirements.txt`
- Make changes
- When committing changes, `black` and `flake8` will be run automatically to ensure code quality
  - In case they don't run automatically, execute `black . && flake8`
  - `black` will automatically make changes to fix any issues it identifies, however the changes would need to be staged again and committed
  - Any problems highlighted by `flake8` requires manual changes/adjustments
- Run the tests to ensure nothing broke
- Push changes, create a pull request