"""
Function to create environment variables and push to git.
"""

import os.path
import sys
from datetime import datetime
from pathlib import Path

import mkdocs_obsidian as obs
from mkdocs_obsidian.common import global_value as gl


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
    BASEDIR = obs.__path__[0]
    try:
        import pyto

        BASEDIR = Path(BASEDIR)
        BASEDIR = BASEDIR.parent.absolute()
    except ModuleNotFoundError:
        pass

    env_path = Path(f"{BASEDIR}/.mkdocs_obsidian")

    print(f"Creating environnement in {env_path}")
    vault = ""
    blog = ""
    while vault == "" or not os.path.isdir(vault):
        vault = str(input("Please provide your obsidian vault path : "))
    while blog == "" or not os.path.isdir(blog):
        blog = str(input("Please provide the blog repository path : "))
    blog_link = check_url(blog).strip()
    if blog_link == "":
        blog_link = str(input("Please, provide the URL of your blog : "))
    share = str(input("Choose your share key name (default: share) : "))
    if share == "":
        share = "share"
    with open(env_path, "w", encoding="utf-8") as env:
        env.write(f"vault={vault}\n")
        env.write(f"blog_path={blog}\n")
        env.write(f"blog={blog_link}\n")
        env.write(f"share={share}\n")
    BASEDIR = gl.BASEDIR
    post = Path(f"{BASEDIR}/docs/notes")
    img = Path(f"{BASEDIR}/docs/assets/img/")
    img.mkdir(exist_ok=True)
    post.mkdir(exist_ok=True)
    sys.exit("Environment created.")


def git_push(commit):
    """
    git push the modified files
    :param commit: str
    :return: None
    """
    try:
        import git

        BASEDIR = gl.BASEDIR
        repo = git.Repo(Path(f"{BASEDIR}/.git"))
        repo.git.add(".")
        repo.git.commit("-m", f"{commit}")
        origin = repo.remote("origin")
        origin.push()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {commit} successfully 🎉")
    except ImportError:
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] {commit} changed\nPlease, use another way to push your change 😶"
        )
