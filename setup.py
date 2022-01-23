#!/usr/bin/env python

from setuptools import find_packages, setup

with open('README.md') as f:
    long_description = f.read()


setup(
    name='trainspotting',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    version='1.0.0',
    license='MIT',
    license_files='LICENSE',
    author='RB387',
    author_email='zavadin142@gmail.com',
    description='Python Dependency Injector based on interface binding',
    url='https://github.com/avito-tech/trainspotting',
    download_url='https://github.com/avito-tech/trainspotting/archive/refs/heads/main.zip',
    keywords=['dependency injection', 'dependency injector', ],
    python_requires='>=3.8',
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: OS Independent',
    ],
    install_requires=[],
)
