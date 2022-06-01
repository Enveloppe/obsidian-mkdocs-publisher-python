"""
Convert one file function.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

import frontmatter
import yaml
from rich.console import Console

from mkdocs_obsidian.common import config as cfg
from mkdocs_obsidian.common import conversion as convert
from mkdocs_obsidian.common import file_checking as check
from mkdocs_obsidian.common import github_push as gitt


def convert_one(
    ori: Path, configuration: cfg.Configuration, git: bool, meta: int, obsidian=False
):
    """Function to start the conversion of *one* specified file."""
    file_name = os.path.basename(ori).upper()
    console = Console()
    try:
        try:
            yaml_front = frontmatter.load(ori, encoding="utf-8")
        except UnicodeDecodeError:
            yaml_front = frontmatter.load(ori, encoding="iso-8859-1")
        priv = configuration.post
        clipkey = configuration.default_folder
        CATEGORY = configuration.category_key
        if CATEGORY in yaml_front.keys():
            if not yaml_front[CATEGORY]:
                priv = check.create_folder("hidden", configuration)
                clipkey = "hidden"
            else:
                priv = check.create_folder(yaml_front[CATEGORY], configuration)
                clipkey = yaml_front[CATEGORY]
        contents = convert.file_convert(configuration, ori, 1)
        checkfile = convert.file_write(configuration, ori, contents, priv, 1, meta)
        if checkfile and git:
            commit = f"Pushed {file_name.lower()} to blog"
            gitt.git_push(commit, configuration, obsidian, "Push", file_name)
            convert.clipboard(configuration, str(ori), clipkey)
        elif checkfile and not git:
            if not obsidian:
                console.print(
                    f"[{datetime.now().strftime('%H:%M:%S')}] 🎉 Successfully converted"
                    f" [u blue bold]{file_name.lower()}[/]"
                )
            else:
                print(
                    f"[{datetime.now().strftime('%H:%M:%S')}] 🎉 Successfully converted"
                    f" {file_name.lower()}"
                )
    except yaml.YAMLError:
        if obsidian:
            print(
                f"Error in {file_name} : Your YAML frontmatter doesn't seem valid! Use"
                " https://jsonformatter.org/yaml-validator to correct it!"
            )
        else:
            print(
                f"Error in [i u]{file_name}[/]: Your YAML frontmatter doesn't seem"
                " valid! Use https://jsonformatter.org/yaml-validator to correct it!"
            )
        sys.exit(2)


def overwrite_file(source_path: str, configuration: cfg.Configuration, test=False):
    """
    Overwrite file with conversion to mkdocs
    """
    from unidecode import unidecode

    filename = os.path.basename(source_path)
    source_path = Path(source_path)
    contents = convert.file_convert(configuration, source_path, 1, False)
    if not test:
        os.remove(source_path)
    if unidecode(filename).replace(".md", "") == unidecode(
        os.path.basename(source_path.parent)
    ):
        source_path = Path(str(source_path).replace(filename, "index.md"))
        filename = "index.md"
    if test:
        source_path = Path(source_path.resolve().parent.parent, "output", "docs", "notes", filename)
    with open(source_path, "w", encoding="utf-8") as new_notes:
        for lines in contents:
            new_notes.write(lines)
    return True
