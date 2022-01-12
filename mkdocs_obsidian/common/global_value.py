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

env_path = Path(f"{BASEDIR}/.mkdocs_obsidian")

if not os.path.isfile(env_path):
    config.create_env()
else:
    with open(env_path, encoding="utf-8") as f:
        components = f.read().splitlines()
        if len(components) == 0:
            config.create_env()
        else:
            for data in components:
                vault = data.split("=")
                if len(data) == 0 or len(vault[1]) == 0:
                    config.create_env()

# In case of error
env = dotenv_values(env_path)
try:
    BASEDIR = Path(env["blog_path"]).expanduser()
    vault = Path(env["vault"]).expanduser()
    web = env["blog"]
    share = env["share"]
except KeyError:
    with open(env_path, "r", encoding="utf-8") as f:
        vault_str = "".join(f.readlines(1)).replace("vault=", "").rstrip()
        basedir_str = "".join(f.readlines(2)).replace("blog_path=", "").rstrip()

        vault = Path(vault_str)
        BASEDIR = Path(basedir_str)
        web = "".join(f.readlines(3)).replace("blog=", "")
        share = "".join(f.readlines(4)).replace("share=", "")
    if len(vault_str) == 0 or len(basedir_str) == 0 or len(web) == 0:
        print("Please provide a valid path for all config items")
        sys.exit(1)
except RuntimeError:
    BASEDIR = Path(env["blog_path"])
    vault = Path(env["vault"])
    web = env["blog"]
    share = env["share"]

try:
    vault = vault.expanduser()
    BASEDIR = BASEDIR.expanduser()
except RuntimeError:
    print("Please, provid a valid path for all config item.")
    sys.exit(1)

if len(share) == 0:
    share = "share"
path = Path(f"{BASEDIR}/.git")  # GIT SHARED
post = Path(f"{BASEDIR}/docs/notes")
img = Path(f"{BASEDIR}/docs/assets/img/")
vault_file = [
    x
    for x in glob.iglob(str(vault) + os.sep + "**", recursive=True)
    if os.path.isfile(x)
]
