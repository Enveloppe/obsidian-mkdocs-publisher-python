"""
Get the environment variables
"""

import glob
import os
import sys
from pathlib import Path

from dotenv import dotenv_values
from rich import print

import mkdocs_obsidian as obs
from mkdocs_obsidian.common import config

BASEDIR = obs.__path__[0]
try:
    import pyto

    BASEDIR = Path(BASEDIR)
    BASEDIR = BASEDIR.parent.absolute()
except ModuleNotFoundError:
    pass

ENV_PATH = Path(f"{BASEDIR}/.mkdocs_obsidian")

if not os.path.isfile(ENV_PATH):
    config.create_env()
else:
    with open(ENV_PATH, encoding="utf-8") as f:
        components = f.read().splitlines()
        if len(components) == 0:
            config.create_env()
        else:
            for data in components:
                VAULT = data.split("=")
                if len(data) == 0 or len(VAULT[1]) == 0:
                    config.create_env()

# In case of error
env = dotenv_values(ENV_PATH)
try:
    BASEDIR = Path(env["blog_path"]).expanduser()
    VAULT = Path(env["vault"]).expanduser()
    WEB = env["blog"]
    try:
        SHARE = env["share"]
    except KeyError:
        SHARE = "share"
        with open(ENV_PATH, "a", encoding="utf-8") as f:
            f.write("share=share")
    try:
        INDEX_KEY = env["index_key"]
    except KeyError:
        INDEX_KEY = "(i)"
        with open(ENV_PATH, "a", encoding="utf-8") as f:
            f.write("index_key=(i)")
    try:
        DEFAULT_NOTES = env["default_blog"]
    except KeyError:
        DEFAULT_NOTES = "notes"
        with open(ENV_PATH, "a", encoding="utf-8") as f:
            f.write("default_blog=notes")
except KeyError:
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        vault_str = "".join(f.readlines(1)).replace("vault=", "").rstrip()
        basedir_str = "".join(f.readlines(2)).replace("blog_path=", "").rstrip()

        VAULT = Path(vault_str)
        BASEDIR = Path(basedir_str)
        WEB = "".join(f.readlines(3)).replace("blog=", "")
        SHARE = "".join(f.readlines(4)).replace("share=", "")
        INDEX_KEY = "".join(f.readlines(5)).replace("index_key=", "")
        DEFAULT_NOTES = "".join(f.readlines(6)).replace("default_blog=", "")
    with open(ENV_PATH, "a", encoding="utf-8") as f:
        if len(SHARE) == 0:
            SHARE = "share"
            f.write("share=share")
        if len(INDEX_KEY) == 0:
            INDEX_KEY = "(i)"
            f.write("index_key=(i)")
        if len(DEFAULT_NOTES) == 0:
            DEFAULT_NOTES = "notes"
            f.write("default_blog=notes")
    if len(vault_str) == 0 or len(basedir_str) == 0 or len(WEB) == 0:
        sys.exit("Please provide a valid path for all config items")
except RuntimeError:
    BASEDIR = Path(env["blog_path"])
    VAULT = Path(env["vault"])
    WEB = env["blog"]
    SHARE = env["share"]
    INDEX_KEY = env["index_key"]
    DEFAULT_NOTES = env["default_blog"]
try:
    VAULT = VAULT.expanduser()
    BASEDIR = BASEDIR.expanduser()
except RuntimeError:
    print('[red bold] Please provide a valid path for all config items')
    sys.exit(3)
if DEFAULT_NOTES == "/":
    DEFAULT_NOTES = ""
POST = Path(f"{BASEDIR}/docs/{DEFAULT_NOTES}")
IMG = Path(f"{BASEDIR}/docs/assets/img/")
VAULT_FILE = [
    x
    for x in glob.iglob(str(VAULT) + os.sep + "**", recursive=True)
    if os.path.isfile(x)
]
