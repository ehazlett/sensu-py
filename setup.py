#!/usr/bin/env python
import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
version = '0.0.1'

setup(
    name='sensu',
    version=version,
    description='Python plugin for the Sensu monitoring framework',
    url='http://github.com/ehazlett/sensu-py',
    download_url=('http://cloud.github.com/downloads/ehazlett/'
                  'sensu-py/sensu-py-%s.tar.gz' % version),
    author='Evan Hazlett',
    author_email='ejhazlett@gmail.com',
    keywords=['sensu', 'plugin', 'monitoring'],
    license='MIT',
    packages=['sensu'],
    install_requires = [ 'requests', 'simplejson' ],
    test_requires = ['mock'],
    test_suite='tests.all_tests',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        ]
)
