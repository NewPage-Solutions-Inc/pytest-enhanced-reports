from setuptools import setup, find_packages

NAME = "enhanced-allure-report"
VERSION = "1.1.0"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools


INSTALL_REQUIRES = [
    "selenium >=4.0.0, <4.1.4",
    "pytest >=6.2.5, < 7.0.0",
    "pytest-bdd >=5.0.0, < 6.0.0",
    "allure-pytest-bdd >=2.9.45, <3.0.0",
    "allure-combine >=1.0.6, <2.0.0",
    "python-dotenv >=0.15.0, <1.0.0",
    "Pillow >=8.4.0, <9.0.0",
    "wrapt >=1.14.1, <2.0.0",
    "opencv-python",
    "pre-commit",
    "black",
    "flake8-noqa",
]

setup(
    name=NAME,
    version=VERSION,
    description="Enhanced allure reports",
    long_description="A enhanced-allure-report to improve allure report by adding screenshots, videos, browser's "
    "outputs",
    author="SDET",
    author_email="qa@newpage.io",
    license="proprietary",
    py_modules=[
        "browser_console_manager",
        "common_utils",
        "enhanced_allure",
        "parameters",
        "screenshot_manager",
        "video_manager",
        "webdriver_event_listener",
    ],
    install_requires=INSTALL_REQUIRES,
    entry_points={"pytest11": ["enhanced_allure_report = enhanced_allure"]},
    classifiers=["Framework :: Pytest"],
)
