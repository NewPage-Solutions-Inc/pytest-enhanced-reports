#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup, find_packages


INSTALL_REQUIRES = [
    "selenium >=4.0.0, <4.1.4",
    "pytest >=6.2.5, < 7.0.0",
    "pytest-bdd >=5.0.0, < 6.0.0",
    "python-dotenv >=0.15.0, <1.0.0",
    "Pillow >=8.4.0, <9.0.0",
    "wrapt >=1.14.1, <2.0.0",
    "opencv-python",
]


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-enhanced-reports',
    version='1.2.3',
    author='NewPage Solutions',
    author_email='InnovationDesk@newpage.io',
    maintainer='NewPage Solutions',
    maintainer_email='InnovationDesk@newpage.io',
    license='MIT',
    url='https://github.com/NewPage-Solutions-Inc/pytest-enhanced-reports',
    description='Enhanced test reports for pytest',
    long_description=read('README.rst'),
    long_description_content_type='text/x-rst',
    keywords='test reports, enhanced reports, screenshot, video, pytest, pytest-bdd, allure, browser logs',
    packages=find_packages(include=['enhanced_reports', 'enhanced_reports.*']),
    include_package_data=True,
    test_suite='tests',
    python_requires='>=3.5',
    install_requires=INSTALL_REQUIRES,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Quality Assurance',
    ],
    entry_points={
        'pytest11': [
            'enhanced_reports = enhanced_reports.core',
        ],
    },
)
