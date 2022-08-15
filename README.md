# enhanced-allure-report

QA innovation project to implement cypress style screenshots and videos for allure reports.
Currently, the implementation is very specific to `pytest-bdd`.

Important Note:
Download the Selenium Chrome from https://chromedriver.chromium.org/downloads. Make sure to unzip it and place the exe file on the root of the project. e.g. in this project, path of your chromedriver file could be "dev/chromedriver".
Once you place the chrome file then use below commands to complete the setup.


1. pip install -r .\requirements.txt



To use the Plugin locally to create screenshot use below commands:
4. Create a wheel file from source by running command ``python3 setup.py bdist_wheel`` inside `/screenshot_plugin` directory
- This command will create a wheel file in `/screenshot_plugin/dist` folder 
- Install this package by running `pip install <path_to_wheel_file>`
