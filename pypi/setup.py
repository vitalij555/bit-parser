import os
from pathlib import Path

import setuptools
from setuptools import setup

ROOT_DIR = Path(__file__).resolve().parents[1]
ROOT_REL = os.path.relpath(ROOT_DIR, Path.cwd())
long_description = (ROOT_DIR / "README.md").read_text(encoding="utf-8")

setup(
    name="bit-parser",
    packages=setuptools.find_packages(where=ROOT_REL),
    package_dir={"": ROOT_REL},
    version="1.0.4",
    license="MIT",
    description="Parse compact bitfields (bitmaps, flag sets) represented as hex strings.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Vitalij Gotovskij",
    author_email="vitalij@cdeveloper.eu",
    url="https://github.com/vitalij555/bit-parser",
    project_urls={
        "Homepage": "https://github.com/vitalij555/bit-parser",
        "Issues": "https://github.com/vitalij555/bit-parser/issues",
    },
    install_requires=[
        "bitops",
    ],
    python_requires=">=3.8",
    keywords=["bit", "bitfield", "bitmap", "protocol", "parser"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
