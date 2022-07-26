"""Setup for pytest-nice plugin."""
from setuptools import setup

setup(
    name='temp_plugin',
    version='0.1.0',
    description='A pytest plugin to take screenshots for allure report',
    author='Shahzad Akram',
    author_email='shahzad.akram@newpage.io',
    license='proprietary',
    py_modules=['temp_plugin'],
    install_requires=[
        "selenium == 4.1.3",
        "pytest == 6.2.5",
        "pytest-bdd == 5.0.0",
        "pytest-selenium == 2.0.1",
        "pytest-selenium-enhancer == 1.7.1",
        "allure-pytest-bdd == 2.9.45",
        "allure-python-commons == 2.9.45",
        "python-dotenv >=0.15.0, <1.0.0",
        "Pillow >=8.4.0, <9.0.0"],
    entry_points={'pytest11': ["temp_plugin = temp_plugin.temp_plugin"], },
    classifiers=["Framework :: Pytest"],
)
