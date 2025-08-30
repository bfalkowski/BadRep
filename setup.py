#!/usr/bin/env python3
"""
Setup script for ReviewLab - Bug-Seeded PR Generator + Review-Accuracy Evaluator
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
with open("requirements.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            requirements.append(line)

setup(
    name="reviewlab",
    version="0.1.0",
    author="ReviewLab Team",
    author_email="team@reviewlab.dev",
    description="Generate PRs with injected bugs and evaluate review bot accuracy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/reviewlab",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/reviewlab/issues",
        "Source": "https://github.com/yourusername/reviewlab",
        "Documentation": "https://reviewlab.readthedocs.io/",
    },
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
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "isort>=5.12.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "reviewlab=cli.main:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="code-review, testing, quality-assurance, bug-injection, evaluation",
)
