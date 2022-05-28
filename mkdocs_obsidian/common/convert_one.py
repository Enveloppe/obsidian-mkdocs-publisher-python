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

from mkdocs_obsidian.common import (
    config as setup,
    conversion as convert,
    file_checking as check,
)


def convert_one(ori, configuration, git, meta, obsidian=False):
    """Function to start the conversion of *one* specified file.

    Parameters
    ----------
    ori: str
        path to file to convert
    configuration: dict
        configuration value with :
        - basedir
        - vault
        - web
        - share
        - index_key
        - default_note
        - post
        - img
        - vault_file
    git: bool
        if True, push to git
    meta: int
        If 1 update the metadata's source file
    obsidian: bool, default: False
        Disable rich markup library

    """

    file_name = os.path.basename(ori).upper()
    console = Console()
    try:
        try:
            yaml_front = frontmatter.load(ori, encoding="utf-8")
        except UnicodeDecodeError:
            yaml_front = frontmatter.load(ori, encoding="iso-8859-1")
        priv = Path(configuration["post"])
        clipkey = configuration["default_note"]
        CATEGORY = configuration["category_key"]
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
            setup.git_push(commit, configuration, obsidian, "Push", file_name)
            convert.clipboard(configuration, ori, clipkey)
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
    sys.exit()


def overwrite_file(source_path: str, configuration: dict):
    """
    Overwrite file with conversion to mkdocs
    Parameters
    ----------
    source_path: str
    configuration: dict
    Returns
    -------

    """
    from unidecode import unidecode

    filename = os.path.basename(source_path)
    shortname = unidecode(os.path.splitext(filename)[0])
    contents = convert.file_convert(configuration, source_path, 1, False)
    os.remove(source_path)
    if shortname == filename:
        filename = "index.md"
    with open(Path(f"{source_path}"), "w", encoding="utf-8") as new_notes:
        for lines in contents:
            new_notes.write(lines)
    return True
