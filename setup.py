#!/usr/bin/env python3

from setuptools import setup, find_namespace_packages

setup(
    name='tdirstat',
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
    url="https://github.com/apockill/tdirstat",
    download_url="https://github.com/apockill/tdirstat/archive/v1.0.0.tar.gz",
    python_requires='>=3.6',
    extras_require={},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
