#############################################################################
#
# Copyright (c) 2011 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from setuptools import setup, find_packages


setup(
    name='z3c.testsummarizer',
    version='2.0',
    author='Stefan Holek, Christian Theune, Wolfgang Schnerring',
    author_email='ws@gocept.com',
    url='',
    description="""\
""",
    long_description=(
        open('README.txt').read()
        + '\n\n'
        + open('CHANGES.txt').read()),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='ZPL 2.1',
    namespace_packages=['z3c'],
    install_requires=[
        'setuptools',
    ],
    extras_require=dict(test=[
    ]),
    entry_points=dict(console_scripts=[
        "test-summarizer = z3c.testsummarizer.main:main",
        "debug-summarizer = z3c.testsummarizer.main:debug"
    ]),
)
