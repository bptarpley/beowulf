#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='wbhb',
    version='2.0',
    description='Bibliography',
    author='Bryan Tarpley',
    author_email='bptarpley@tamu.edu',
    license='BSD',
    install_requires=[
        'django',
        'mysqlclient',
        'django-tinymce'
    ],
    packages=find_packages(),
    #package_data={'dashboard.emop.static' : ['*'],},
    #include_package_data=True,
    #zip_safe=False,
)
