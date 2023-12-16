#!/usr/bin/env python3
import os
from setuptools import setup
from os import walk, path

URL = "https://github.com/OpenVoiceOS/ovos-docs-viewer"
PYPI_NAME = "ovos-docs-viewer"  # pip install PYPI_NAME

# below derived from github url to ensure standard skill_id
AUTHOR, NAME = URL.split(".com/")[-1].split("/")

with open("README.md", "r") as f:
    long_description = f.read()

def get_version():
    """ Find the version of this skill"""
    version_file = os.path.join(os.path.dirname(__file__), 'version.py')
    major, minor, build, alpha = (None, None, None, None)
    with open(version_file) as f:
        for line in f:
            if 'VERSION_MAJOR' in line:
                major = line.split('=')[1].strip()
            elif 'VERSION_MINOR' in line:
                minor = line.split('=')[1].strip()
            elif 'VERSION_BUILD' in line:
                build = line.split('=')[1].strip()
            elif 'VERSION_ALPHA' in line:
                alpha = line.split('=')[1].strip()

            if ((major and minor and build and alpha) or
                    '# END_VERSION_BLOCK' in line):
                break
    version = f"{major}.{minor}.{build}"
    if int(alpha):
        version += f"a{alpha}"
    return version

setup(
    name=PYPI_NAME,
    version=get_version(),
    long_description=long_description,
    url=URL,
    author=AUTHOR,
    description='Useful scripts for OVOS',
    author_email='jarbasai@mailfence.com',
    license='Apache-2.0',
    install_requires=[
        'click',
        'requests',
        'textual',
        'ovos_utils'
        ],
    keywords='ovos scripts',
    entry_points={
        'console_scripts': [
            'doc_viewer = ovos_docs_viewer.ovos_docs:launch'
            ]
        }
)
