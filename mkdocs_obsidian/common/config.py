"""
Function to create environment variables and push to git.
"""

import glob
import os.path
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from time import sleep

from dotenv import dotenv_values
from rich import print
from rich.console import Console
from rich.markdown import Markdown

import mkdocs_obsidian as obs


def pyto_environment(console):
    """(IOS) Use Pyto [1]_ bookmark to get folder path

    Parameters
    ----------
    console :
        rich console

    Returns
    -------
    tuple [str, str]:
         vault:
            vault absolute path
         blog:
            Blog absolute path

    References
    -------
    .. [1] https://pyto.readthedocs.io/en/latest/library/bookmarks.html
    """
    import bookmarks as bm

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
    """(Other platform) Ask environment ; rely only on console.

    Parameters
    ----------
    console :
        rich console

    Returns
    -------
    tuple [str, str]:
        vault:
            vault absolute path
        blog:
            Blog absolute path
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
    """Create environment for computer (Windows, Linux, macOS) using filedialog (tkinter) and askdirectory.
    Parameters
    ----------
    console :
        rich console

    Returns
    -------
    tuple [str, str]:
        vault:
            vault absolute path
        blog:
            Blog absolute path

    """
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
    (IOS) Use pickFolder [1]_ in **ashell** to help to create the environment

    Parameters
    ----------
    console:
        rich console

    Returns
    -------
    tuple [str, str]:
        vault:
            vault absolute path
        blog:
            Blog absolute path

    References
    ----------
    .. [1] https://github.com/holzschu/a-shell#sandbox-and-bookmarks

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


def check_url(blog_path):
    """check if the url is in the config file and return it

    Parameters
    ----------
    blog_path : str
        Publish absolute path

    Returns
    -------
    web: str
        Site url founded in site_url from mkdocs.yml
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
    """
    Check if .obsidian exist in provided vault path
    Parameters
    ----------
    vault: str
        Absolute path to vault

    Returns
    -------
    bool:
        return True .obsidian exist in vault
    """
    config_vault = os.path.join(vault, ".obsidian")
    if os.path.isdir(config_vault):
        return True
    return False


def create_env(config_name="0"):
    """
    Main function to create environment ; Check if run on pyto (IOS), a-shell (ios) or computer (MacOS, linux, Windows)

    Create environment variable with asking for :
        - blog_link : Publish url if not found
        - share : Metadata key for sharing file
        - default_blog : Default folder for notes

    Write the variable in `.env` file.
    Parameters
    ----------
    config_name: str, default: "0"
        Create a new configuration environment using the provided name
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
    if config_name == "0":
        config_name = ".mkdocs_obsidian"
    else:
        config_name = "." + config_name
    env_path = Path(f"{BASEDIR}/{config_name}")
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
    default_blog = console.input(
        "Choose your default folder note [i](default: [bold]notes[/])[/]: "
    )
    if default_blog == "":
        default_blog = "notes"
    if share == "":
        share = "share"
    index_key = str(
        console.input(
            "If you want to use [u]folder note[/], please choose the key for citation"
            " [i](default: [bold](i)[/])[/]: "
        )
    )
    category_key = str(
        console.input(
            "Please, choose the key for the category [i](default:"
            " [bold]category[/])[/]: "
        )
    )
    if category_key == "":
        category_key = "category"
    if index_key == "":
        index_key = "(i)"
    with open(env_path, "w", encoding="utf-8") as env:
        env.write(f"vault={vault}\n")
        env.write(f"blog_path={blog}\n")
        env.write(f"blog={blog_link}\n")
        env.write(f"share={share}\n")
        env.write(f"index_key={index_key}\n")
        env.write(f"default_blog={default_blog}\n")
        env.write(f"category_key={category_key}\n")
    if default_blog == "/":
        default_blog = ""
    post = Path(f"{blog}/docs/{default_blog}")
    img = Path(f"{blog}/docs/assets/img/")
    try:
        img.mkdir(
            exist_ok=True
        )  # Assets must exist, raise a file not found error if not.
        post.mkdir(exist_ok=True, parents=True)
        print("[green] Environment created ![/]")
        sys.exit()
    except FileNotFoundError:
        print("[red bold] Error in configuration, please, retry with the correct path.")
        sys.exit(3)


def git_pull(configuration, git=True):
    """
    Command to pull the repository
    if no_git or import error : pass
    Parameters
    ----------
    configuration: dict
        Dictionary containing the basedir
    git: bool, default: true
        If true, pull the repo
    """
    console = Console()
    if git:
        try:
            import git

            BASEDIR = configuration["basedir"]
            try:
                repo = git.Repo(Path(f"{BASEDIR}"))
                update = repo.remotes.origin
                update.pull()
                return True
            except git.GitCommandError as exc:
                console.print(f"Unexpected error : {exc}", style="bold white on red")
                return False
        except ImportError:
            return False


def git_push(
    commit,
    configuration,
    obsidian=False,
    add_info="",
    rmv_info="",
    add_msg="",
    remove_msg="",
):
    """
    git push the modified files and print a message result

    Parameters
    ----------
    commit: str
        Commit information
    configuration: dict
    obsidian : bool, default: False
        Message without markup
    add_info : str, default: ""
        Adding title
    rmv_info : str, default: ""
        Removing title
    remove_msg : str, default: ""
        File removed
    add_msg : str, default: ""
    """
    console = Console()
    try:
        import git

        BASEDIR = configuration["basedir"]
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
                if add_msg != "":
                    add_msg = ": " + add_msg
                if remove_msg != "":
                    remove_msg = ": " + remove_msg
                print(
                    f"🎉 Successful 🎉",
                    f"[{datetime.now().strftime('%H:%M:%S')}]\n",
                    f"{add_info}{add_msg}",
                    f"{rmv_info}{remove_msg}",
                )
        except git.GitCommandError:
            if not obsidian:
                console.print(
                    f"❌ Nothing to Push ❌",
                    "[[i not bold"
                    f" sky_blue2]{datetime.now().strftime('%H:%M:%S')}][/]\n",
                    "💡 Converted 💡",
                    f" {add_info}",
                    Markdown(add_msg),
                    rmv_info,
                    Markdown(remove_msg),
                    end=" ",
                )
            else:
                if remove_msg != "":
                    remove_msg = ": " + remove_msg
                print(
                    f"❌ Nothing to Push ❌\n",
                    f"[{datetime.now().strftime('%H:%M:%S')}]",
                    "💡 Converted 💡\n",
                    f"{add_msg}",
                    f"{rmv_info}{remove_msg}",
                )
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


def open_value(configuration_name="0", actions=False):
    """
    Return the configuration value
    Parameters
    ----------
    configuration_name: str
        The configuration name. If "0", use the default configuration, aka : .mkdocs_obsidian ;
        Else use ".configuration_name"
    actions: bool, default: False
        If run in github actions
    Returns
    -------
    dict [Path, Path, str, str, str, str, Path, Path, list[str]]:
        - basedir: Path
        - vault : Path
        - web: str
        - share: str
        - index_key: str
        - default_note: str
        - post: Path
            Post folder absolute path
        - img : Path
            Image folder absolute path
        - vault_file: list[str]
            List of all files in vault
    """
    BASEDIR = obs.__path__[0]
    try:
        import pyto

        BASEDIR = Path(BASEDIR)
        BASEDIR = BASEDIR.parent.absolute()
    except ModuleNotFoundError:
        pass
    if actions:
        BASEDIR = Path(os.getcwd())
        VAULT = ""
        WEB = ""
        SHARE = ""
    elif configuration_name == "0":
        configuration_name = ".mkdocs_obsidian"
    else:
        configuration_name = "." + configuration_name
    if not actions:
        ENV_PATH = Path(f"{BASEDIR}/{configuration_name}")
    else:
        ENV_PATH = Path(BASEDIR, "source", ".github-actions")
    if not os.path.isfile(ENV_PATH):
        create_env()
    elif not actions:
        with open(ENV_PATH, encoding="utf-8") as f:
            components = f.read().splitlines()
            if len(components) == 0:
                create_env()
            else:
                for data in components:
                    VAULT = data.split("=")
                    if len(data) == 0 or len(VAULT[1]) == 0:
                        create_env()

    # In case of error
    env = dotenv_values(ENV_PATH)
    try:
        if not actions:
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
        try:
            CATEGORY = env["category_key"]
        except KeyError:
            CATEGORY = "category"
            with open(ENV_PATH, "a", encoding="utf-8") as f:
                f.write("category_key=category")
    except KeyError:
        with open(ENV_PATH, "r", encoding="utf-8") as f:

            if not actions:
                vault_str = "".join(f.readlines(1)).replace("vault=", "").rstrip()
                basedir_str = "".join(f.readlines(2)).replace("blog_path=", "").rstrip()
                BASEDIR = Path(basedir_str)
                WEB = "".join(f.readlines(3)).replace("blog=", "")
                SHARE = "".join(f.readlines(4)).replace("share=", "")
            INDEX_KEY = "".join(f.readlines(5)).replace("index_key=", "")
            DEFAULT_NOTES = "".join(f.readlines(6)).replace("default_blog=", "")
            CATEGORY = "".join(f.readlines(7)).replace("category_key=", "")
        with open(ENV_PATH, "a", encoding="utf-8") as f:
            if len(SHARE) == 0 and not actions:
                SHARE = "share"
                f.write("share=share")
            if len(INDEX_KEY) == 0:
                INDEX_KEY = "(i)"
                f.write("index_key=(i)")
            if len(DEFAULT_NOTES) == 0:
                DEFAULT_NOTES = "notes"
                f.write("default_blog=notes")
            if len(CATEGORY) == 0:
                CATEGORY = "category"
                f.write("category_key=category")
        if (
            len(vault_str) == 0
            or len(basedir_str) == 0
            or len(WEB) == 0
            and not actions
        ):
            sys.exit("Please provide a valid path for all config items")
    except RuntimeError:
        if not actions:
            BASEDIR = Path(env["blog_path"])
            VAULT = Path(env["vault"])
            WEB = env["blog"]
            SHARE = env["share"]
        INDEX_KEY = env["index_key"]
        DEFAULT_NOTES = env["default_blog"]
        CATEGORY = env["category_key"]
    try:
        if not actions:
            VAULT = VAULT.expanduser()
            BASEDIR = BASEDIR.expanduser()
    except RuntimeError:
        print("[red bold] Please provide a valid path for all config items")
        sys.exit(3)
    if DEFAULT_NOTES == "/":
        DEFAULT_NOTES = ""
    POST = Path(f"{BASEDIR}/docs/{DEFAULT_NOTES}")
    IMG = Path(f"{BASEDIR}/docs/assets/img/")
    if actions:
        VAULT_FILE = [
            x
            for x in glob.iglob(
                str(os.getcwd()) + os.sep + "source" + os.sep + "**", recursive=True
            )
            if os.path.isfile(x)
        ]
    else:
        VAULT_FILE = [
            x
            for x in glob.iglob(str(VAULT) + os.sep + "**", recursive=True)
            if os.path.isfile(x)
        ]
    configuration = {
        "basedir": Path(BASEDIR),
        "vault": Path(VAULT),
        "web": WEB,
        "share": SHARE,
        "index_key": INDEX_KEY,
        "default_note": DEFAULT_NOTES,
        "post": POST,
        "img": IMG,
        "vault_file": VAULT_FILE,
        "category_key": CATEGORY,
    }
    return configuration
