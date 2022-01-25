"""
Function to create environment variables and push to git.
"""

import os.path
import sys
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich import print
import mkdocs_obsidian as obs
from mkdocs_obsidian.common import global_value as gl


def check_url(blog_path: str):
    """
    check if the url is in the config file and return it
    :param blog_path: Publish absolute path
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
    console = Console()
    print(f"[bold]Creating environnement in [u]{env_path}[/][/]")
    vault = ""
    blog = ""
    while vault == "" or not os.path.isdir(vault):
        vault = str(
            console.input("Please provide your [u bold]obsidian vault[/] path: ")
        )
    while blog == "" or not os.path.isdir(blog):
        blog = str(
            console.input("Please provide the [u bold]blog[/] repository path: ")
        )
    blog_link = check_url(blog).strip()
    if blog_link == "":
        blog_link = str(console.input("Please, provide the [u]URL[/] of your blog: "))
    share = str(
        console.input("Choose your share key name [i](default: [bold]share[/])[/]: ")
    )
    if share == "":
        share = "share"
    index_key = str(
        input(
            "If you want to use [u]folder note[/], please choose the key for citation"
            " [i](default: [bold](i)[/])[/]: "
        )
    )
    if index_key == "":
        index_key = "(i)"
    with open(env_path, "w", encoding="utf-8") as env:
        env.write(f"vault={vault}\n")
        env.write(f"blog_path={blog}\n")
        env.write(f"blog={blog_link}\n")
        env.write(f"share={share}\n")
        env.write(f"index_key={index_key}\n")
    BASEDIR = gl.BASEDIR
    post = Path(f"{BASEDIR}/docs/notes")
    img = Path(f"{BASEDIR}/docs/assets/img/")
    img.mkdir(exist_ok=True)
    post.mkdir(exist_ok=True)
    sys.exit("Environment created.")


def git_push(commit: str):
    """
    git push the modified files and print a message result
    :param commit: Commit information
    :return: None
    """
    console = Console()
    try:
        import git

        BASEDIR = gl.BASEDIR
        repo = git.Repo(Path(f"{BASEDIR}/.git"))
        repo.git.add(".")
        repo.git.commit("-m", f"{commit}")
        origin = repo.remote("origin")
        origin.push()
        console.print(
            f"[{datetime.now().strftime('%H:%M:%S')}]",
            Markdown(commit),
            "successfully 🎉",
            end=" ",
        )

    except ImportError:
        console.print(
            f"[{datetime.now().strftime('%H:%M:%S')}]",
            Markdown(commit),
            "changed\nPlease, use another way to push your change 😶",
            end=" ",
        )
