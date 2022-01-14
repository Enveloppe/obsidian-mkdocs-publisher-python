"""
Get the environment variables
"""

from pathlib import Path
import sys
import glob
import os
from dotenv import dotenv_values

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
    SHARE = env["share"]
except KeyError:
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        vault_str = "".join(f.readlines(1)).replace("VAULT=", "").rstrip()
        basedir_str = "".join(f.readlines(2)).replace("blog_path=", "").rstrip()

        VAULT = Path(vault_str)
        BASEDIR = Path(basedir_str)
        WEB = "".join(f.readlines(3)).replace("blog=", "")
        SHARE = "".join(f.readlines(4)).replace("share=", "")
    if len(vault_str) == 0 or len(basedir_str) == 0 or len(WEB) == 0:
        sys.exit("Please provide a valid path for all config items")
except RuntimeError:
    BASEDIR = Path(env["blog_path"])
    VAULT = Path(env["vault"])
    WEB = env["blog"]
    SHARE = env["share"]

try:
    VAULT = VAULT.expanduser()
    BASEDIR = BASEDIR.expanduser()
except RuntimeError:
    sys.exit("Please provide a valid path for all config items")

if len(SHARE) == 0:
    SHARE = "share"

POST = Path(f"{BASEDIR}/docs/notes")
IMG = Path(f"{BASEDIR}/docs/assets/img/")
VAULT_FILE = [
    x
    for x in glob.iglob(str(VAULT) + os.sep + "**", recursive=True)
    if os.path.isfile(x)
]
