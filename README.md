# allure-screenshots
QA innovation project to implement cypress style screenshots for allure reports.

Important Note:
1. First of all you need to download the Selenium Chrome from https://chromedriver.chromium.org/downloads. Make sure to unzip it and place the exe file on the root of the project. e.g. in this project, path of your chromedriver file could be "dev/chromedriver". 

2. Create a .env file under root folder and add below variables with the value of your choice for screenshots:
SCREENSHOT_HEIGHT=800
SCREENSHOT_WIDTH=600


Once you place the chrome file then use below commands to complete the setup.

Helping commands to run tests on Windows/Mac, just install the package requirements and launch the test:
1. pip install -r requirements\requirements.txt 
2. pytest

Helping commands to run tests and generate Allure report:
1. pytest -v -s --alluredir=reports --driver Chrome --driver-path dev/chromedriver
2. allure serve reports

If you want to send different values for the screenshot size then check the below command as an example:
SCREENSHOT_HEIGHT=2040 SCREENSHOT_WIDTH=1080 pytest -v -s --alluredir=reports --driver Chrome --driver-path dev/chromedriver

If you want to send percentage value of screenshot resolution then use below command:
pytest -v -s -q —image reduction 100 dev/test/step_defs —alluredir=reports --driver Chrome --driver-path dev/chromedriver
