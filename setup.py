"""
Setup configuration for dlswidow-scraper package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="dlswidow-scraper",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A robust and configurable social media scraper built with Python and Selenium",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dlswidow-scraper",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "selenium>=4.15.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "PyYAML>=6.0.0",
        "loguru>=0.7.0",
        "python-dateutil>=2.8.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config/*.yaml"],
    },
)