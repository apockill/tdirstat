#!/usr/bin/env python3

from setuptools import setup, find_namespace_packages

setup(
    name='alex-tools',
    version='0.1.0',
    description="A random set of commandline tools for my personal use",
    packages=find_namespace_packages(
        include=["tools*"]
    ),
    author="Alex Thiel",
    scripts=[],
    entry_points={
        "console_scripts": {
            "axls=tools:ls",
            "axexplore=tools:file_explorer",
            "tdirstat=tools.tdirstat:tdirstat"
        }
    },
    install_requires=[
        "asciimatics==1.11.0"
    ],

    extras_require={}

)
