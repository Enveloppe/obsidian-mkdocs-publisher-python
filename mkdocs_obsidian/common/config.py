"""
Function to create environment variables and push to git.
"""

import glob
import os.path
import platform
import subprocess
import sys
from pathlib import Path
from time import sleep

import yaml
from dotenv import dotenv_values
from rich import print
from rich.console import Console

import mkdocs_obsidian as obs


class Configuration:
    def __init__(
        self,
        output: str|Path,
        input: str|Path,
        weblink: str,
        share_key: str,
        index_key:str,
        default_folder: str,
        post: Path|str,
        img: Path|str,
        vault_file: list[str],
        category_key: str,
    ):
        self.output = Path(output)
        self.input = Path(input) if input else ''
        self.weblink = weblink
        self.share_key = share_key
        self.index_key = index_key
        self.default_folder = default_folder
        self.post = Path(post)
        self.img = Path(img)
        self.vault_file = vault_file
        self.category_key = category_key


def pyto_environment(console: Console) -> tuple[str, str]:
    """(IOS) Use Pyto [1]_ bookmark to get folder path
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


def legacy_environment(console: Console) -> tuple[str, str]:
    """(Other platform) Ask environment ; rely only on console."""
    vault = ""
    blog = ""
    while vault == "" or not os.path.isdir(vault) or not right_path(Path(vault)):
        vault = str(
            console.input("Please provide your [u bold]obsidian vault[/] path: ")
        )
    while blog == "" or not os.path.isdir(blog):
        blog = str(
            console.input("Please provide the [u bold]blog[/] repository path: ")
        )
    return vault, blog


def PC_environment(console: Console) -> tuple[str, str]:
    """Create environment for computer (Windows, Linux, macOS) using filedialog (tkinter) and askdirectory."""
    import tkinter.filedialog

    vault = ""
    blog = ""
    while vault == "" or not right_path(Path(vault)):
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


def ashell_environment(console: Console) -> tuple[str, str]:
    """
    (IOS) Use pickFolder [1]_ in **ashell** to help to create the environment
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


def check_url(blog_path: Path) -> str:
    """check if the url is in the config file and return it"""
    web = ""
    try:
        blog_path = blog_path.expanduser()
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


def right_path(vault: Path) -> bool:
    """
    Check if .obsidian exist in provided vault path
    """
    config_vault = Path(vault, ".obsidian")
    if os.path.isdir(config_vault):
        return True
    return False


def create_env( BASEDIR: Path, config_name="0"):
    """
    Main function to create environment ; Check if run on pyto (IOS), a-shell (ios) or computer (MacOS, linux, Windows)

    Create environment variable with asking for :
        - blog_link : Publish url if not found
        - share : Metadata key for sharing file
        - default_blog : Default folder for notes

    Write the variable in `.env` file.
    """
    try:
        import pyto

        pyto_check = True
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
        config_name = "default"
    env_path = Path(f"{BASEDIR}/configuration.yml")
    print(f"[bold]Creating environnement in [u]{env_path}[/][/] for [u]{config_name}[/]\n")
    if pyto_check:
        vault, blog = pyto_environment(console)
    elif ashell:
        vault, blog = ashell_environment(console)
    elif computer:
        vault, blog = PC_environment(console)
    else:
        vault, blog = legacy_environment(console)
    blog_link = check_url(Path(blog)).strip()
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
    new_configuration = {
        'weblink' : blog_link,
        'configuration':{
            'input' : vault,
            'output': blog,
            },
        'frontmatter':
             {
                 'share' : share,
                 'index' : index_key,
                 'category' : {
                     'key' : category_key,
                     'default value': default_blog
                     }
             }
        }
    if default_blog == "/":
        default_blog = ""
    adding_configuration(config_name, BASEDIR, new_configuration)
    post = Path(f"{blog}/docs/{default_blog}")
    img = Path(f"{blog}/docs/assets/img/")
    try:
        img.mkdir(
            exist_ok=True
        )  # Assets must exist, raise a file not found error if not.
        post.mkdir(exist_ok=True, parents=True)
        print("[green] Environment created ![/]")
    except FileNotFoundError:
        print("[red bold] Error in configuration, please, retry with the correct path.")
        sys.exit(3)
    return


def convert_to_YAML(BASEDIR: Path, ENV_PATH: Path, configuration: Configuration, type="default"):
    template = f'''
    weblink: {configuration.weblink}
    configuration:
        input: {configuration.input}
        output : {configuration.output}
    frontmatter:
        share: {configuration.share_key}
        index: {configuration.index_key}
        category:
            key: {configuration.category_key}
            default value: {configuration.default_folder}
    '''
    new_configuration = yaml.safe_load(template)
    adding_configuration(configuration_name=type, basedir=BASEDIR, new_configuration=new_configuration)
    os.remove(ENV_PATH)

def adding_configuration(configuration_name: str, basedir: Path, new_configuration: dict):
    env_file = Path(basedir, 'configuration.yml')
    if os.path.isfile(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            configuration_contents = yaml.safe_load(f)
        configuration_contents[configuration_name] = new_configuration
    else:
        configuration_contents = {configuration_name: new_configuration}
    configuration_contents = yaml.dump(configuration_contents)
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(configuration_contents)


def checking_old_config(configuration_name: str, ENV_PATH: Path, basedir: Path):
    env = dotenv_values(ENV_PATH)
    try:
        BASEDIR = Path(env["blog_path"]).resolve().expanduser() if env.get("blog_path") else ""
        VAULT = Path(env["vault"]).resolve().expanduser() if env.get('vault') else ""
    except RuntimeError:
        print('[red blog] Please provide a valid path for all config items')
        sys.exit(3)
    WEB = env.get("blog", "")
    SHARE = env.get('share', 'share')
    INDEX_KEY = env.get('index_key', '(i)')
    DEFAULT_NOTES = env.get('default_blog', 'notes')
    CATEGORY_KEY = env.get('category_key', 'category')
    if DEFAULT_NOTES == "/":
        DEFAULT_NOTES = ""
    new_config = Configuration(BASEDIR, VAULT, WEB, SHARE, INDEX_KEY, DEFAULT_NOTES, "", "", [], CATEGORY_KEY)
    convert_to_YAML(basedir, ENV_PATH, new_config, configuration_name)

def get_Obs2mk_dir(configuration_name="default", actions=False) -> Path:
    BASEDIR = obs.__path__[0]
    try:
        import pyto

        BASEDIR = Path(BASEDIR)
        BASEDIR = BASEDIR.parent.absolute()
    except ModuleNotFoundError:
        pass
    if actions or configuration_name == "minimal" or 'test' in configuration_name:
        BASEDIR = Path(os.getcwd())
        if 'test' in configuration_name:
            BASEDIR = Path(BASEDIR, "docs_tests", "output")
    return BASEDIR

def open_value(configuration_name="default", actions=False) -> Configuration:
    """
    Return the configuration value
    """
    BASEDIR=get_Obs2mk_dir(configuration_name, actions)
    if 'test' in configuration_name:
        if 'minimal' in configuration_name:
            configuration_name = "minimal"
        else:
            configuration_name = "default"
        ENV_PATH = Path(BASEDIR, '.obs2mk')
    elif actions:
        ENV_PATH = Path(BASEDIR, "source", ".github-actions")
    else:
        if configuration_name == "default":
            ENV_PATH = Path(f"{BASEDIR}/.mkdocs_obsidian")
        else:
            ENV_PATH = Path(f"{BASEDIR}/.{configuration_name}")

    if os.path.isfile(ENV_PATH):
        checking_old_config(configuration_name, ENV_PATH, BASEDIR)
    ENV_PATH = Path(BASEDIR, 'configuration.yml')
    if not os.path.isfile(ENV_PATH):
        create_env(BASEDIR, configuration_name)
    with open (ENV_PATH, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    if not config.get(configuration_name):
        create_env(BASEDIR, configuration_name)
    config = config[configuration_name]
    BASEDIR = Path(config['configuration']['output']).resolve().expanduser() if config['configuration'].get('output') else BASEDIR
    VAULT = Path(config['configuration']['input']).resolve().expanduser() if config['configuration'].get('input') else ""
    WEB = config['weblink']
    SHARE= config['frontmatter']['share']
    INDEX_KEY = config['frontmatter']['index']
    CATEGORY = config['frontmatter']['category']['key']
    DEFAULT_NOTES = config['frontmatter']['category']['default value']
    if DEFAULT_NOTES == "/":
        DEFAULT_NOTES = ""
    POST = Path(BASEDIR, "docs", DEFAULT_NOTES)
    IMG = Path(BASEDIR, "/docs/assets/img/")
    if actions == "minimal":
        VAULT_FILE = [
            x
            for x in glob.iglob(str(Path(os.getcwd(), "docs", "**")), recursive=True)
            if os.path.isfile(x)
        ]
    elif actions:
        VAULT_FILE = [
            x
            for x in glob.iglob(str(Path(os.getcwd(), "source", "**")), recursive=True)
            if os.path.isfile(x)
        ]
    else:
        VAULT_FILE = [
            x
            for x in glob.iglob(str(Path(VAULT, "**")), recursive=True)
            if os.path.isfile(x)
        ]
    configuration = Configuration(
        BASEDIR,
        VAULT,
        WEB,
        SHARE,
        INDEX_KEY,
        DEFAULT_NOTES,
        POST,
        IMG,
        VAULT_FILE,
        CATEGORY,
    )
    return configuration
