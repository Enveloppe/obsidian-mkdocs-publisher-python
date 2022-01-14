"""
Convert one file function.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

import frontmatter
import yaml

from mkdocs_obsidian.common import (
    file_checking as check,
    conversion as convert,
    config as setup,
    global_value as value,
)


def convert_one(ori, git, meta):
    """
    Function to start the conversion of *one* specified file.
    :param ori: str
    :param git: bool
    :param meta: int
    :return: None
    """
    file_name = os.path.basename(ori).upper()
    try:
        yaml_front = frontmatter.load(ori)
        priv = Path(value.POST)
        clipkey = "notes"
        if yaml_front.get("category"):
            priv = check.create_folder(yaml_front["category"])
            clipkey = yaml_front["category"]
        contents = convert.file_convert(ori, 1)
        checkfile = convert.file_write(ori, contents, priv, 1, meta)
        if checkfile and not git:
            commit = f"Pushed {file_name.lower()} to blog"
            setup.git_push(commit)
            convert.clipboard(ori, clipkey)
        elif checkfile and git:
            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] 🎉 Successfully converted {file_name.lower()}"
            )
    except yaml.YAMLError:
        sys.exit(
            f"Error in {file_name} : Your YAML frontmatter doesn't seem valid! Use https://jsonformatter.org/yaml-validator to correct it!"
        )
    sys.exit()
