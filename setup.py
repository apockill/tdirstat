#!/usr/bin/env python3

from setuptools import setup, find_namespace_packages

setup(
    name='alex-tools',
    version='1.0.0',
    description="Terminal-based directory statistics with a nice TUI and quick"
                " actionable information",
    packages=find_namespace_packages(
        include=["tdirstat*"]
    ),
    author="Alex Thiel",
    scripts=[],
    entry_points={
        "console_scripts": {
            "tdirstat=tdirstat:tdirstat"
        }
    },
    install_requires=[
        "asciimatics==1.11.0"
    ],
    extras_require={}
)
