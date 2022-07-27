"""Setup for pytest-nice plugin."""
from setuptools import setup

setup(
    name='allure-screenshot',
    version='0.1.0',
    description='A pytest plugin to take screenshots for allure report',
    author='Waleed',
    author_email='muhammad.waleed@newpage.io',
    license='proprietary',
    py_modules=['allure_screenshot',"settings"],
    install_requires=[
        "selenium",
        "pytest",
        "pytest-bdd",
        "allure-pytest-bdd",
        "python-dotenv >=0.15.0, <1.0.0",
        "Pillow >=8.4.0, <9.0.0"],
    entry_points={'pytest11': ["allurescreenshot = allure_screenshot"]},
    classifiers=["Framework :: Pytest"],
)
