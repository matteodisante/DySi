"""Setup script for rocket-simulation package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

setup(
    name="rocket-simulation",
    version="0.1.0",
    author="STARPI Team",
    author_email="",
    description="Modular rocket dynamics simulation framework using RocketPy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/starpi/rocket-simulation",
    packages=find_packages(where="."),
    package_dir={"": "."},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "rocketpy>=1.2.0",
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "matplotlib>=3.4.0",
        "pyyaml>=6.0",
        "pandas>=1.3.0",
        "h5py>=3.6.0",
        "simplekml>=1.3.6",
        "pytz>=2021.3",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "mypy>=0.950",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "ipython>=8.0.0",
        ],
        "notebooks": [
            "jupyter>=1.0.0",
            "jupyterlab>=3.0.0",
            "ipywidgets>=7.6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "rocket-sim=scripts.run_single_simulation:main",
            "rocket-mc=scripts.run_monte_carlo:main",
        ],
    },
)
