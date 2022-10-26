# Enhanced Allure Report

----
## Introduction
A library which enhances allure report by adding screenshots, videos, browser's output in the original report.

## Supported Python Versions
- Python 3.7+

## Installing
If you have pip on your system, you can simply install or upgrade the Python bindings:
```bash
pip install -U enhanced-allure-report/
```

Alternately, run this command in the root directory:
```bash
python setup.py install
```

## Example 1: run tests with screenshots captured
```bash
pytest --alluredir=reports --driver Chrome \
  --driver-path dev/chromedriver \
  --report_screenshot_resize_percent 50
```

## Example 2: run tests with videos captured
```bash
pytest -v -s -q dev/test/step_defs/ --alluredir=reports \
  --driver Chrome \ 
  --driver-path dev/chromedriver \
  --report_video_recording true
```

## Example 3: run tests with browser's outputs captured
```bash
pytest --alluredir=reports \
  --driver-path deb/chromedriver \
  --variables capabilities.json \
  --driver Chrome \
  --variables capabilities.json \
  --always_capture_log=True
```

## Usage
We provided 2 different way to use configuration:
- commandline parameters
- environment arguments
  
Please refer to the tables below for supported flags 

### Screenshots
| Flag                                      | Expected Value              | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|-------------------------------------------|-----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| <b>--report_screenshot_level</b>          | 'all', 'none', 'error-only' | This flag is used to enable Screenshot capturing. If value is not specified, it will default to <b>all</b>.                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| <b>--report_screenshot_width</b>          | Number                      | Used to set the width of the screenshot. (the actual width of the image used in reports could be different depending on the aspect ratio of the image)                                                                                                                                                                                                                                                                                                                                                                                        |
| <b>--report_screenshot_height</b>         | Number                      | Used to set the height of the screenshot. (the actual height of the image used in reports could be different depending on the aspect ratio of the image)                                                                                                                                                                                                                                                                                                                                                                                      |
| <b>--report_screenshot_resize_percent</b> | Number                      | - Used to resize/reduce the height and width of original screenshot to a specific percentage.<br> - If --report_screenshot_width and report_image_resize_height are given along with this flag then this flag will not have any effect.<br>- If --report_screenshot_width and height are not given but this flag is provided then screenshot will be resized to this percentage.<br>- If neither --report_screenshot_width, report_image_resize_height nor report_image_resize_percentage is given then <b>this flag will default to 30%</b>. |
| <b>--report_screenshot_dir</b>            | directory name              | Used to write the screenshots to attach with allure report. <b>It will default to `/screenshots`</b> if not specified by user.                                                                                                                                                                                                                                                                                                                                                                                                                |
| <b>--report_keep_screenshots</b>          | true, false                 | Used to enable user to keep the original screenshots in `screenshots/` or user provided directory                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| <b>--report_highlight_element</b>         | true, false                 | Used to highlight element and take a screenshot before user's interaction                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |

### Video-Recording
| Flag                                    | Expected Value | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
|-----------------------------------------|----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| <b>--report_video_recording</b>         | true, false    | This flag is used to enable video recording. If value is not specified, it will default to <b>false</b>.                                                                                                                                                                                                                                                                                                                                                                           |
| <b>--report_video_width</b>             | Number         | Used to set the width of the video frame.                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| <b>--report_video_height</b>            | Number         | Used to set the height of the video frame.                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| <b>--report_video_resize_percentage</b> | Number         | - Used to resize/reduce the height and width of original frames to a specific percentage.<br> - If --report_video_width and video_height are given along with this flag then this flag will not have any effect.<br>- If --report_video_width and height are not given but this flag is provided then frame will be resized to this percentage.<br>- If neither --report_video_width, video_height nor video_resize_percentage is given then <b>this flag will default to 30%</b>. |
| <b>--report_video_frame_rate</b>        | Number         | Used to set the number of frames per second in the video. <b>It will default to 5 fps</b> if not specified by user.                                                                                                                                                                                                                                                                                                                                                                |
| <b>--report_video_dir</b>               | directory name | Used to write the videos to attach with allure report. <b>It will default `/videos`</b> if not specified by user.                                                                                                                                                                                                                                                                                                                                                                  |
| <b>--report_keep_videos</b>             | true, false    | Used to enable user to keep the videos in `videos/` or user provided directory                                                                                                                                                                                                                                                                                                                                                                                                     |

### Browser's outputs
| Flag                                        | Expected Value            | Description                                                   |
|---------------------------------------------|---------------------------|---------------------------------------------------------------|
| <b>--report_capture_browser_console_log</b> | always, never, on_failure | This flag is used to enable capturing browser's outputs.</b>. |


## Contributing
- Create a branch for your work
- After making changes, before committing execute `black . && flake8`
- `flake8` requires manual fixes
- `black` will often rewrite the breakages automatically, however the files are unstaged and should be staged again.
