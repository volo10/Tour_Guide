#!/usr/bin/env python3
"""
Setup script for Tour Guide package.

This file is for backwards compatibility with older pip versions.
The main configuration is in pyproject.toml.
"""

from setuptools import setup, find_packages

setup(
    name="tour-guide",
    version="1.0.0",
    description="A tour guide system providing personalized recommendations for driving routes",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Tour Guide Team",
    url="https://github.com/volo10/Tour_Guide",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[],
    extras_require={
        "rest": ["flask>=2.0.0"],
        "dev": ["pytest>=7.0.0", "black>=23.0.0"],
    },
    entry_points={
        "console_scripts": [
            "tour-guide=tour_guide.user_api.cli:run_cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
