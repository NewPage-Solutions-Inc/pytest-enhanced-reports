# allure-screenshots
QA innovation project to implement cypress style screenshots and video recording for allure reports.

Important Note:
Download the Selenium Chrome from https://chromedriver.chromium.org/downloads. Make sure to unzip it and place the exe file on the root of the project. e.g. in this project, path of your chromedriver file could be "dev/chromedriver".
Once you place the chrome file then use below commands to complete the setup.

### Installing 'allure-screenshot'

Helping commands to run tests on Windows/Mac, just install the package requirements and launch the test:
1. pip install -r requirements.txt 
2. pytest
3. To install plugin remotely, below commands are useful depending on the repository access:
   1. If repo is public: <br>`pip install git+https://github.com/userabc/allurescreenshotplugin.git/`
   2. If repo is private, you may use your private token:<br> `pip install git+https://{PRIVATE_TOKEN}@github.com/userabc/allurescreenshotplugin.git/`
   3. If you want to use ssh:<br> `pip install git+ssh://git@github.com/userabc/allurescreenshotplugin.git`

### Usage

#### Screenshots:
Once plugin is installed then you may pass level of screenshots to be taken for allure reporting.


| Flag                                      | Expected Value              | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|-------------------------------------------|-----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| <b>--report_screenshot_level</b>          | 'all', 'none', 'error-only' | This flag is used to enable Screenshot capturing. If value is not specified, it will default to <b>all</b>.                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| <b>--report_screenshot_width</b>          | Number                      | Used to set the width of the screenshot. (the actual width of the image used in reports could be different depending on the aspect ratio of the image)                                                                                                                                                                                                                                                                                                                                                                                        |
| <b>--report_screenshot_height</b>         | Number                      | Used to set the height of the screenshot. (the actual height of the image used in reports could be different depending on the aspect ratio of the image)                                                                                                                                                                                                                                                                                                                                                                                      |
| <b>--report_screenshot_resize_percent</b> | Number                      | - Used to resize/reduce the height and width of original screenshot to a specific percentage.<br> - If --report_screenshot_width and report_image_resize_height are given along with this flag then this flag will not have any effect.<br>- If --report_screenshot_width and height are not given but this flag is provided then screenshot will be resized to this percentage.<br>- If neither --report_screenshot_width, report_image_resize_height nor report_image_resize_percentage is given then <b>this flag will default to 30%</b>. |


- if you pass argument "screenshot_option" with value "all", then screenshot will be taken for each step in scenario:<br> 
 `pytest --alluredir=reports --driver Chrome --driver-path /chromedriver --report_screenshot_level all`

- if you pass argument "screenshot_option" with value "fail", then screenshot will be taken for only failed steps in scenario:<br> 
 `pytest --alluredir=reports --driver Chrome --driver-path dev/chromedriver --report_screenshot_level fail`

- you pass argument "screenshot_option" with value "none", then no screenshot will be shown to the allure report: 
 `pytest --alluredir=reports --driver Chrome --driver-path dev/chromedriver --report_screenshot_level none`

- If you want to send image width and image height for the screenshot size in allure report then you can use "report_image_resize_width" and "report_image_resize_height" arguments with your desired values, and below command can be used as an example:
 `pytest --report_screenshot_width 720 --report_screenshot_height 1080  --alluredir=reports --driver Chrome --driver-path dev/chromedriver`
- If you want to reduce percentage size of the image to be taken for allure screenshot then you may send "report_screenshot_resize_percent" with your desired value, and below is the helping command:
 `pytest --alluredir=reports --driver Chrome --driver-path dev/chromedriver --report_screenshot_resize_percent 50`                                 

#### Video-Recording:

1. In pytest execution command, following video related flags can be used to enable video recording.
2. Below-mentioned flags can be used to enable vide recording and set width and height.
3. These flags can be used with flags of screenshots. Video flags will have no effect on the screenshot captures.

##### Available Flags:

| Flag                                    | Expected Value | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
|-----------------------------------------|----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| <b>--report_video_recording</b>         | true, false    | This flag is used to enable video recording. If value is not specified, it will default to <b>false</b>.                                                                                                                                                                                                                                                                                                                                                                           |
| <b>--report_video_width</b>             | Number         | Used to set the width of the video frame.                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| <b>--report_video_height</b>            | Number         | Used to set the height of the video frame.                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| <b>--report_video_resize_percentage</b> | Number         | - Used to resize/reduce the height and width of original frames to a specific percentage.<br> - If --report_video_width and video_height are given along with this flag then this flag will not have any effect.<br>- If --report_video_width and height are not given but this flag is provided then frame will be resized to this percentage.<br>- If neither --report_video_width, video_height nor video_resize_percentage is given then <b>this flag will default to 30%</b>. |
| <b>--report_video_frame_rate</b>        | Number         | Used to set the number of frames per second in the video. <b>It will default to 5 fps</b> if not specified by user.                                                                                                                                                                                                                                                                                                                                                                |

##### Examples:
1. Enable video recording with default settings:<br>
``pytest -v -s -q dev/test/step_defs/ --alluredir=reports/runUpdatedVideoSingleThread --driver Chrome --driver-path /Users/mwaleedz/PycharmProjects/allure-screenshot/allure-screenshots/dev/chromedriver --report_video_recording true``<br>This command will generate video and by default reduce its frame width and height to 30%.
2. Enable video recording with <b>--report_video_width and --report_video_height</b> flags:<br>``pytest -v -s -q dev/test/step_defs/ --alluredir=reports/runUpdatedVideoSingleThread --driver Chrome --driver-path /Users/mwaleedz/PycharmProjects/allure-screenshot/allure-screenshots/dev/chromedriver --report_video_recording true ----report_video_width 1920 --report_video_height 1080``<br>This command will generate video with specified height and width.
3. Enable video recording with <b>--report_video_resize_percentage</b>:<br>``pytest -v -s -q dev/test/step_defs/ --alluredir=reports/runUpdatedVideoSingleThread --driver Chrome --driver-path /Users/mwaleedz/PycharmProjects/allure-screenshot/allure-screenshots/dev/chromedriver --report_video_recording true --video_resize_percentage 50``<br>This command will generate video and by default reduce its frame width and height to 50%.
4. Enable video recording with <b>--report_video_width, --report_video_height, --report_video_frame_rate</b> flags:<br>``pytest -v -s -q dev/test/step_defs/ --alluredir=reports/runUpdatedVideoSingleThread --driver Chrome --driver-path /Users/mwaleedz/PycharmProjects/allure-screenshot/allure-screenshots/dev/chromedriver --report_video_recording true ----report_video_width 1920 --report_video_height 1080 --report_video_frame_rate 10``<br>This command will generate video with specified height and width with 10 frames per second.

#### View Reports
2. After running any of above commands, you can check the Allure report (you may use any of below commands):
- allure serve reports
- allure generate reports

To use the Plugin locally to create screenshot use below commands:
4. Create a wheel file from source by running command ``python3 setup.py bdist_wheel`` inside `/screenshot_plugin` directory
- This command will create a wheel file in `/screenshot_plugin/dist` folder 
- Install this package by running `pip install <path_to_wheel_file>`

pytest -v -s -q dev/test/step_defs/ --report_screenshot_level all --report_screenshot_width 720 --report_screenshot_height 1080  --alluredir=reports --driver Chrome --driver-path dev/chromedriver


--------------------------------------------------------------------------------------------------------
Important note:
Make sure your conftest file has fixture for web driver like below:

@pytest.fixture
def selenium(selenium, resize_info):
    selenium.maximize_window()
    driver = EventFiringWebDriver(selenium, WebDriverEventListener(resize_info))
    yield driver
    driver.quit()
---------------------------------------------------------------------------------------------------------