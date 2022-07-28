# allure-screenshots
QA innovation project to implement cypress style screenshots for allure reports.

Important Note:
Download the Selenium Chrome from https://chromedriver.chromium.org/downloads. Make sure to unzip it and place the exe file on the root of the project. e.g. in this project, path of your chromedriver file could be "dev/chromedriver".
Once you place the chrome file then use below commands to complete the setup.

Install the Plugin:
(Install the wheel dependencies mentioned in requirement.txt file first)
1. Create a wheel file from source by running command ``python3 setup.py bdist_wheel`` inside `/screenshot_plugin` directory
2. This command will create a wheel file in `/screenshot_plugin/dist` folder
3. Install this package by running `pip install <path_to_wheel_file>`

Helping commands to run tests on Windows/Mac, just install the package requirements and launch the test:
1. pip install -r requirements\requirements.txt 
2. pytest
- If you want to send image width and image height for the screenshot size in allure report then you can use "report_image_resize_width" and "report_image_resize_height" arguments with your desired values, and below command can be used as an example:
 `pytest -v -s -q dev/test/step_defs/  --report_image_resize_width 720 --report_image_resize_height 1080  --alluredir=reports --driver Chrome --driver-path dev/chromedriver`

- If you want to reduce percentage size of the image to be taken for allure screenshot then you may send "report_image_resize_to_percent" with your desired value, and below is the helping command:
 ``pytest -v -s -q --report_image_resize_to_percent 50 dev/test/step_defs/ --alluredir=reports --driver Chrome --driver-path dev/chromedriver``                                 

3. After running any of above commands, you can check the Allure report (you may use any of below commands):
- allure serve reports
- allure generate reports
