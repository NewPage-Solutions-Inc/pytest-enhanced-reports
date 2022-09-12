from setuptools import setup

setup(
    name='enhanced-allure-report',
    version='0.2.2',
    description='A pytest plugin to take screenshots for allure report',
    author='SDET',
    author_email='qa@newpage.io',
    license='proprietary',
    py_modules=['enhanced_allure', 'allure_screenshot', 'allure_video_recording', 'common_utils'],
    install_requires=[
        "selenium >=4.0.0, <4.1.4",
        "pytest >=6.2.5, < 7.0.0",
        "pytest-bdd >=5.0.0, < 6.0.0",
        "allure-pytest-bdd >=2.9.45, <3.0.0",
        "allure-combine >=1.0.6, <2.0.0",
        "python-dotenv >=0.15.0, <1.0.0",
        "Pillow >=8.4.0, <9.0.0",
        "wrapt >=1.14.1, <2.0.0",
        "opencv-python",
    ],
    entry_points={'pytest11': ["enhanced_allure_report = enhanced_allure"]},
    classifiers=["Framework :: Pytest"],
)