# allure-screenshots
QA innovation project to implement cypress style screenshots for allure reports.

Helping commands to run tests on Windows/Mac, just install the package requirements and launch the test:
1. pip install -r requirements\requirements.txt
2. pytest

Helping commands to generate Allure report:
1. pytest -v -s --alluredir=allure_report 
2. allure serve "allure_report"

