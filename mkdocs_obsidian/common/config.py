from pathlib import Path
import sys
import glob
import os
from datetime import datetime
from dotenv import dotenv_values

import mkdocs_obsidian as obs

BASEDIR = obs.__path__[0]
try:
    import pyto
    BASEDIR=Path(BASEDIR)
    BASEDIR=BASEDIR.parent.absolute()
except ModuleNotFoundError:
    pass
    
env_path = Path(f"{BASEDIR}/.mkdocs_obsidian")


def check_url(blog_path):
    """
    check if the url is in the config file and return it
    :param blog_path: Path
    :return: URL
    """
    web = ""
    try:
        blog_path = Path(blog_path).expanduser()
    except RuntimeError:
        blog_path = Path(blog_path)
    mkdocs = Path(f"{blog_path}/mkdocs.yml")
    try:
        with open(mkdocs, "r", encoding="utf-8") as mk:
            for i in mk:
                if "site_url:" in i:
                    web = i.replace("site_url:", "")
    except FileNotFoundError:
        pass
    return web


def create_env():
    """
    Create environment variable with:
        - vault = Path to the obsidian vault ;
        - blog = Path to the publish folder
        - blog_link = Publish url
        - share = Metadata key for sharing file
    :return: None
    """
    print(f"Creating environnement in {env_path}")
    env = open(env_path, "w", encoding="utf-8")
    vault = ""
    blog = ""
    while vault == "":
        vault = str(input("Please provide your obsidian vault path : "))
    while blog == "":
        blog = str(input("Please provide the blog repository path : "))
    blog_link = check_url(blog).strip()
    if blog_link == "":
        blog_link = str(input("Please, provide the URL of your blog : "))
    share = str(input("Choose your share key name (default: share) : "))
    if share == "":
        share = "share"
    env.write(f"vault={vault}\n")
    env.write(f"blog_path={blog}\n")
    env.write(f"blog={blog_link}\n")
    env.write(f"share={share}\n")
    env.close()


if not os.path.isfile(env_path):
    create_env()
else:
    with open(env_path) as f:
        components = f.read().splitlines()
        if len(components) == 0:
            create_env()
        else:
            for data in components:
                vault = data.split("=")
                if len(data) == 0 or len(vault[1]) == 0:
                    create_env()


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
img.mkdir(exist_ok=True)
post.mkdir(exist_ok=True)
vault_file = [
    x
    for x in glob.iglob(str(vault) + os.sep + "**", recursive=True)
    if os.path.isfile(x)
]


def git_push(COMMIT):
    """
    git push the modified files
    :param COMMIT: str
    :return: None
    """
    try:
        import git

        repo = git.Repo(Path(f"{BASEDIR}/.git"))
        repo.git.add(".")
        repo.git.commit("-m", f"{COMMIT}")
        origin = repo.remote("origin")
        origin.push()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {COMMIT} successfully 🎉")
    except ImportError:
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] {COMMIT} changed\nPlease, use another way to push your change 😶"
        )
