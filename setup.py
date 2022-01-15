from setuptools import setup, find_packages

version = "1.2.6"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name="obs2mk",
    python_requires=">=3.7",
    version=version,
    description="A script to share your obsidian vault (in partial way) using mkdocs",
    author="Mara-Li",
    author_email="mara-li@icloud.com",
    packages=find_packages(),
    install_requires=[
        "python-dotenv",
        "gitpython",
        "python-frontmatter",
        "pyYAML",
        "pyperclip",
        "unidecode",
    ],
    license="AGPL",
    keywords="obsidian, obsidian.md, free publish, publish, mkdocs, material",
    classifiers=[
        "Natural Language :: English",
        "Natural Language :: French",
        "Topic :: Text Processing :: Markup :: Markdown",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Mara-Li/mkdocs_obsidian_publish",
    entry_points={
        "console_scripts": ["obs2mk=mkdocs_obsidian.__main__:main"],
    },
)
