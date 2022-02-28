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
    file_checking as check,
    conversion as convert,
    config as setup,
    global_value as value,
    )


def convert_one(ori, git: bool, meta: int, obsidian=False):
    """Function to start the conversion of *one* specified file.

    Parameters
    ----------
    ori: str
        path to file to convert
    git: Bool
        if True, push to git
    meta: int
        If 1 update the metadata's source file
    obsidian: Bool, default: False
        Disable rich markup library

    """
    file_name = os.path.basename(ori).upper()
    console = Console()
    try:
        yaml_front = frontmatter.load(ori)
        priv = Path(value.POST)
        clipkey = value.DEFAULT_NOTES
        if "category" in yaml_front.keys():
            if not yaml_front["category"]:
                priv = check.create_folder("hidden")
                clipkey = "hidden"
            else:
                priv = check.create_folder(yaml_front["category"])
                clipkey = yaml_front["category"]
        contents = convert.file_convert(ori, 1)
        checkfile = convert.file_write(ori, contents, priv, 1, meta)
        if checkfile and git:
            commit = f"Pushed {file_name.lower()} to blog"
            setup.git_push(commit, obsidian, "Push", file_name)
            convert.clipboard(ori, clipkey)
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
            print(f"Error in {file_name} : Your YAML frontmatter doesn't seem valid! Use"
            " https://jsonformatter.org/yaml-validator to correct it!")
        else:
            print(f"Error in [i u]{file_name}[/]: Your YAML frontmatter doesn't seem valid! Use"
            " https://jsonformatter.org/yaml-validator to correct it!")
        sys.exit(2)
    sys.exit()
