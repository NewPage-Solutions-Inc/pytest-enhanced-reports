# allure-screenshots
QA innovation project to implement cypress style screenshots for allure reports.

First of all you need to download the Selenium Chrome from https://chromedriver.chromium.org/downloads. Make sure to unzip it and place the exe file on the root of the project. e.g. in this project, path of your chromedriver file could be "dev/chromedriver". Once you place the chrome file then use below commands to complete the setup.

Helping commands to run tests on Windows/Mac, just install the package requirements and launch the test:
1. pip install -r requirements\requirements.txt 
2. pytest

Helping commands to run tests and generate Allure report:
1. pytest -v -s --alluredir=reports --driver Chrome --driver-path dev/chromedriver
2. allure serve reports