"""
Function to create environment variables and push to git.
"""

import os.path
import subprocess
import sys
from datetime import datetime
from time import sleep
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich import print
import mkdocs_obsidian as obs
import platform


def pyto_environment(console):
    """
    Use pyto bookmark to get path on IOS
    :param console: rich console
    :return vault_path ; blog_path
    """
    import bookmarks as bm

    vault = ""
    blog = ""
    console.print("Please provide your [u bold]obsidian vault[/] path: ")
    sleep(5)  # The user needs to read the message !
    vault = bm.FolderBookmark()
    vault_path = vault.path
    console.print(f"[u]Vault:[/][i] {vault_path}[/]\n")
    console.print("Please provide the [u bold]blog[/] repository path: ")
    sleep(5)  # The user needs to read the message !
    blog = bm.FolderBookmark()
    blog_path = blog.path
    console.print(f"[u]Blog:[/][i] {blog_path}[/]\n")
    return vault_path, blog_path


def legacy_environment(console):
    """
    Ask environment without using pyto bookmark
    :param console: rich console
    :return vault_path, blog_path
    """
    vault = ""
    blog = ""
    while vault == "" or not os.path.isdir(vault) or not right_path(vault):
        vault = str(
            console.input("Please provide your [u bold]obsidian vault[/] path: ")
        )
    while blog == "" or not os.path.isdir(blog):
        blog = str(
            console.input("Please provide the [u bold]blog[/] repository path: ")
        )
    return vault, blog


def PC_environment(console):
    import tkinter.filedialog

    vault = ""
    blog = ""
    while vault == "" or not right_path(vault):
        console.print("Please provide your [u bold]obsidian vault[/] path")
        sleep(1)
        vault = tkinter.filedialog.askdirectory()
    console.print(f"[u]Vault:[/][i] {vault}[/]\n")
    while blog == "":
        console.print("Please provide the [u bold]blog[/] repository path")
        sleep(1)
        blog = tkinter.filedialog.askdirectory()
    console.print(f"[u]Blog:[/][i] {blog}[/]\n")
    return vault, blog


def ashell_environment(console):
    """
    Relly on pickFolder in ashell to create the environment
    :param console: rich console
    :return vault_path, blog_path
    """
    console.print("Please provide your [u bold]obsidian vault[/] path: ")
    cmd = "pickFolder"
    sleep(5)  # The user needs to read the message !
    subprocess.Popen(cmd, stdout=subprocess.PIPE)
    sleep(10)
    console.input("Press any key to continue...")
    # Now, the os.getcwd() change for the pickedFolder
    vault = os.getcwd()
    sleep(3)
    console.print(f"[u]Vault:[/][i] {vault}[/]\n")
    console.print("Please provide the [u bold]blog[/] repository path: ")
    sleep(3)  # The user needs to read the message !
    subprocess.Popen(cmd, stdout=subprocess.PIPE)
    sleep(10)
    console.input("Press any key to continue...")
    blog = os.getcwd()
    console.print(f"[u]Blog:[/][i] {blog}[/]\n")
    # return to default environment
    cmd = "cd ~/Documents"
    subprocess.Popen(cmd, stdout=subprocess.PIPE)
    sleep(3)
    return vault, blog


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


def right_path(vault):
    config_vault = os.path.join(vault, ".obsidian")
    if os.path.isdir(config_vault):
        return True
    return False


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

        pyto_check = True
        BASEDIR = Path(BASEDIR)
        BASEDIR = BASEDIR.parent.absolute()
    except ModuleNotFoundError:
        pyto_check = False
    try:
        import subprocess

        process = subprocess.Popen("echo $TERM_PROGRAM", stdout=subprocess.PIPE)
        output, error = process.communicate()
        ashell = output.decode("utf-8").strip() == "a-Shell"
    except (RuntimeError, FileNotFoundError):
        ashell = False
    computer = False
    if platform.architecture()[1] != "":
        computer = True
    console = Console()
    env_path = Path(f"{BASEDIR}/.mkdocs_obsidian")
    print(f"[bold]Creating environnement in [u]{env_path}[/][/]\n")
    if pyto_check:
        vault, blog = pyto_environment(console)
    elif ashell:
        vault, blog = ashell_environment(console)
    elif computer:
        vault, blog = PC_environment(console)
    else:
        vault, blog = legacy_environment(console)
    blog_link = check_url(blog).strip()
    if blog_link == "":
        blog_link = str(console.input("Please, provide the [u]URL[/] of your blog: "))
    share = str(
        console.input("Choose your share key name [i](default: [bold]share[/])[/]: ")
    )
    if share == "":
        share = "share"
    index_key = str(
        console.input(
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
    post = Path(f"{blog}/docs/notes")
    img = Path(f"{blog}/docs/assets/img/")
    try:
        img.mkdir(
            exist_ok=True
        )  # Assets must exist, raise a file not found error if not.
        post.mkdir(
            exist_ok=True, parents=True
        )  # Notes is needed in this configuration ;
        sys.exit("Environment created.")
    except FileNotFoundError:
        sys.exit("Error in configuration, please, retry with the correct path. ")


def git_push(
    commit: str, obsidian=False, add_info="", rmv_info="", add_msg="", remove_msg=""
):
    """
    git push the modified files and print a message result
    :param commit: Commit information
    :param obsidian: Message without markup
    :param add_info: Adding title
    :param rmv_info: Removing title
    :param remove_msg: File removed
    :param add_msg: File added/modified
    :return: None
    """
    console = Console()
    try:
        import git
        from mkdocs_obsidian.common import global_value as gl

        BASEDIR = gl.BASEDIR
        try:
            repo = git.Repo(Path(f"{BASEDIR}/.git"))
            repo.git.add(".")
            repo.git.commit("-m", f"{commit}")
            origin = repo.remote("origin")
            origin.push()
            if not obsidian:
                console.print(
                    f"[[i not bold sky_blue2]{datetime.now().strftime('%H:%M:%S')}][/]"
                    f" {add_info}",
                    Markdown(add_msg),
                    rmv_info,
                    Markdown(remove_msg),
                    Markdown("---"),
                    "🎉 Successful 🎉",
                    end=" ",
                )
            else:
                print(
                    f" 🎉 Successful 🎉 [{datetime.now().strftime('%H:%M:%S')}]"
                    f" {add_info}:{add_msg}\n{rmv_info}:{remove_msg}\n"
                )
        except git.GitCommandError:
            if not obsidian:
                console.print(
                    f"[[i not bold sky_blue2]{datetime.now().strftime('%H:%M:%S')}[/]]",
                    Markdown("*No modification 😶*"),
                    end=" ",
                )
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] No modification 😶")
    except ImportError:
        if not obsidian:
            console.print(
                f"[{datetime.now().strftime('%H:%M:%S')}]",
                Markdown(commit),
                "changed\nPlease, use another way to push your change 😶",
                end=" ",
            )
        else:
            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] {commit} changed\n Please use"
                " another way to push your change 😶"
            )
