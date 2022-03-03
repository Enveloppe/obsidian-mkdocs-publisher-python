from setuptools import setup, find_packages

version = "3.0.0"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt") as f:
    required = f.read().splitlines()
setup(
    name="obs2mk",
    python_requires=">=3.9",
    version=version,
    description="A script to share your obsidian vault (in partial way) using mkdocs",
    author="Mara-Li",
    author_email="mara-li@icloud.com",
    packages=find_packages(),
    install_requires=required,
    license="AGPL",
    keywords="obsidian, obsidian.md, free publish, publish, mkdocs, material",
    classifiers=[
        "Natural Language :: English",
        "Natural Language :: French",
        "Topic :: Text Processing :: Markup :: Markdown",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later"
        " (AGPLv3+)",
        "Programming Language :: Python :: 3.9",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Mara-Li/mkdocs_obsidian_publish",
    entry_points={
        "console_scripts": ["obs2mk=mkdocs_obsidian.__main__:main"],
    },
)
