from pathlib import Path
import os
from datetime import datetime
from dotenv import dotenv_values

import mkdocs_obsidian as obs

BASEDIR = obs.__path__[0]
env_path = Path(f"{BASEDIR}/.mkdocs_obsidian")


def create_env():
    print(f"Creating environnement in {env_path}")
    env = open(env_path, "w", encoding="utf-8")
    vault = ""
    blog = ""
    blog_link = ""
    share = "share"
    while vault == "":
        vault = str(input("Please provide your obsidian vault path : "))
    while blog == "":
        blog = str(input("Please provide the blog repository path : "))
        while blog_link == "":
            blog_link = str(
                input("Please provide the blog link (as https://yourblog.github.io) : ")
            )
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
    with open(env_path) as f:
        vault_str = "".join(f.readlines(1)).replace("vault=", "").rstrip()
        basedir_str = "".join(f.readlines(2)).replace("blog_path=", "").rstrip()

        vault = Path(vault_str)
        BASEDIR = Path(basedir_str)
        web = "".join(f.readlines(3)).replace("blog=", "")
        share = "".join(f.readlines(4)).replace("share=", "")
    if len(vault_str) == 0 or len(basedir_str) == 0 or len(web) == 0:
        print("Please provide a valid path for all config items")
        exit(1)
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
    exit(1)

if len(share) == 0:
    share = "share"
path = Path(f"{BASEDIR}/.git")  # GIT SHARED
post = Path(f"{BASEDIR}/docs/notes")
img = Path(f"{BASEDIR}/docs/assets/img/")
img.mkdir(exist_ok=True)
post.mkdir(exist_ok=True)


def git_push(COMMIT):
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
            f"[{datetime.now().strftime('%H:%M:%S')}] Please, use another way to push your change 😶"
        )
