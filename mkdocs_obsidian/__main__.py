import argparse
import os
import sys
import textwrap
from datetime import datetime
from pathlib import Path

from rich import print
from rich.console import Console
from rich.markdown import Markdown

try:
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

from mkdocs_obsidian.common import (
    convert_all as all,
    convert_one as one,
    file_checking as check,
)


def search_shortcuts(VAULT_FILE, file):
    """

    Parameters
    ----------
    VAULT_FILE: list[str]
        All file in vault
    file: str
        filepath or filename
    Returns
    -------
    str|bool:
        False if file not found ; filepath otherwise
    """
    if not file.endswith(".md"):
        file = file + ".md"
    for md in VAULT_FILE:
        if os.path.basename(md) == os.path.basename(file):
            return md
    return False


def obsidian_shell(
    configuration, file="0", meta_update=0, vault_share=0, git=True, delete_option=False
):
    """
    Just run the CLI without python rich, for printing in Obsidian Shell
    Parameters
    ----------
    configuration: dict
    file: str
    meta_update: int, default: 0
    vault_share: int, default: 0
    git: bool, default: True
    delete_option: bool, default: False

    """
    VAULT_FILE = configuration["vault_file"]
    if file == "0":
        all.obsidian_simple(configuration, delete_option, git, 1, 0, vault_share)
    elif not os.path.exists(Path(file)):
        file = search_shortcuts(VAULT_FILE, file)
        if not file:
            print("File not found.")
            sys.exit(1)
        one.convert_one(file, configuration, git, meta_update, True)
    elif file != "0" and os.path.exists(Path(file)):
        one.convert_one(file, configuration, git, meta_update, True)
    sys.exit()


def mobile_shortcuts(
    configuration, file="0", meta_update=0, vault_share=0, delete_option=False
):
    """
    - Never use git
    - Can search a file in vault with the filename
    Parameters
    ----------
    configuration: dict
    file: str
    meta_update: int, default: 0
    vault_share: int, default: 0
    delete_option: bool, default: False

    Returns
    -------

    """
    from mkdocs_obsidian.common import config as setup

    VAULT_FILE = configuration["vault_file"]
    if file == "0":
        all.convert_all(configuration, delete_option, False, 1, 0, vault_share)
    elif not os.path.exists(Path(file)):
        file = search_shortcuts(VAULT_FILE, file)
        if not file:
            print("[u red]File not found.")
            sys.exit(1)
        one.convert_one(file, configuration, False, meta_update)
    elif file == "--c":
        setup.create_env()
    elif file != "0" and os.path.exists(Path(file)):
        one.convert_one(file, configuration, False, meta_update)


def keep(obsidian, console, configuration, actions=False):
    """
    Delete the file moved or removed from sharing
    Parameters
    ----------
    obsidian: bool
        If using obsidian shell or not
    console:
        Rich console
    configuration: dict
    actions: bool, default: False
        If we want to clean using github actions.
    Returns
    -------
    int
    """
    info = check.delete_not_exist(configuration, actions)
    if len(info) > 1:
        info_str = "\n- " + "\n- ".join(info)
        if not obsidian:
            console.print(
                f'[[i not bold sky_blue2]{datetime.now().strftime("%H:%M:%S")}[/]]'
                " 🗑️[u red bold]Delete from blog :[/]",
                Markdown(info_str),
                end="",
            )
        else:
            print(
                f'[{datetime.now().strftime("%H:%M:%Sf")}] 🗑️ Delete from blog:'
                f" {info_str}"
            )
    elif len(info) == 1:
        info_str = info[0]
        if not obsidian:
            console.print(
                f"🗑️ [u red bold] Delete[/] [bold red i] {info_str}[/] [u red"
                " bold]from blog[/]"
            )
        else:
            print(f"Delete {info_str} from blog.")
    return 1


def main():
    """
    Main function using in CLI
    Global options :
        - --git : No commit and push to git ;
        - --mobile : Use mobile shortcuts instead of `--git`
        - --meta : Update frontmatter of source files
        - --keep : Don't delete files in blog folder
        - --shell : Remove Rich printing
    Commands and specific options :
        - configuration :
            - --new configuration_name : Create a specific configuration for some files
        - all : Share all vault
            - --force : Force updating
        - vault: Share all file in vault
            - --force : Force updating
        - file [file] : Share only one file

    :return: None
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """Global options :
        - --git : No commit and push to git ;
        - --mobile : Use mobile shortcuts instead of `--git`
        - --meta : Update frontmatter of source files
        - --keep : Don't delete files in blog folder
        - --shell : Remove Rich printing
        - --GA: Specify the usage of the script in a github action. 
    Commands and specific options : 
        - configuration :
            - --new configuration_name : Create a specific configuration for some files
        - clean: Clean all removed files
        - publish : Share all vault
            - --force : Force updating
            - --vault : Share all vault file, ignoring the share state.
        - file [file] : Share only one file
        """
        ),
    )

    subparser = parser.add_subparsers(dest="cmd")
    config = subparser.add_parser(
        "config",
        help=(
            "Configure the script : Add or edit your vault and blog absolute path,"
            " change some keys."
        ),
    )
    config.add_argument(
        "--new",
        help="Create a new configuration",
        action="store",
        metavar="configuration_name",
    )
    publish = subparser.add_parser("all", help="Publish multiple files")
    publish.add_argument(
        "--force", action="store_true", help="Force updating all files"
    )
    publish.add_argument(
        "--vault",
        action="store_true",
        help="Publish all file in your vault, ignoring the share state. ",
    )

    files_cmd = subparser.add_parser("file", help="Publish only one file")
    files_cmd.add_argument("filepath", action="store")
    clean = subparser.add_parser("clean", help="Clean all removed files")
    group_git = parser.add_mutually_exclusive_group()
    group_git.add_argument(
        "--mobile",
        "--shortcuts",
        help="Use mobile shortcuts, without push",
        action="store_true",
    )
    group_git.add_argument(
        "--git", "--g", "--G", help="No commit and no push to git", action="store_false"
    )

    parser.add_argument(
        "--meta",
        "--m",
        "--M",
        help="Update the frontmatter of the source file with the link to the note",
        action="store_false",
    )
    parser.add_argument(
        "--keep",
        "--k",
        "--K",
        help="Keep deleted file from vault and removed shared file",
        action="store_true",
    )
    parser.add_argument(
        "--use",
        "--config",
        help="Use a different config from default",
        action="store",
        metavar="configuration_name",
    )
    parser.add_argument(
        "--obsidian", "--shell", help=argparse.SUPPRESS, action="store_true"
    )
    parser.add_argument(
        "--GA", "--actions", help=argparse.SUPPRESS, action="store_true"
    )
    console = Console()
    args = parser.parse_args()
    from mkdocs_obsidian.common import config as setup

    cmd = args.cmd

    configuration_name = args.use or "0"
    if cmd == "config":
        configuration_name = args.new or "0"
        setup.create_env(configuration_name)
        sys.exit()
    elif cmd == "clean":
        configuration = setup.open_value(configuration_name, args.GA)
        if not args.git and not args.GA:
            setup.git_pull(configuration, args.git)
        keep(args.obsidian, console, configuration, args.GA)
        if not args.git and not args.GA:
            setup.git_push(
                "clean all removed files",
                configuration,
                args.obsidian,
                rmv_info="Clean all removed files",
            )
    else:
        configuration = setup.open_value(configuration_name, args.GA)
        meta_update = int(args.meta)
        no_git = args.git
        if not args.keep:
            stop_share = keep(args.obsidian, console, configuration, args.GA)
        else:
            stop_share = 0
        if cmd == "file":
            file_source = args.filepath
            if args.obsidian:
                setup.git_pull(configuration, no_git)
                obsidian_shell(configuration, file_source, meta_update, git=no_git)
                sys.exit()
            elif args.mobile or args.GA:
                mobile_shortcuts(configuration, file_source, meta_update)
                sys.exit()
            elif os.path.exists(Path(file_source)):
                setup.git_pull(configuration, no_git)
                one.convert_one(file_source, configuration, no_git, meta_update)
            else:
                console.print(
                    f"ERROR: {file_source} doesn't exist", style="bold white on red"
                )
                sys.exit(1)

        elif cmd == "all":
            vault_share = int(args.vault)
            delete_option = args.force
            if args.mobile:
                mobile_shortcuts(
                    configuration, "0", meta_update, vault_share, delete_option
                )
            elif args.obsidian:
                setup.git_pull(configuration, no_git)
                obsidian_shell(
                    configuration, "0", meta_update, vault_share, no_git, delete_option
                )
            else:
                setup.git_pull(configuration, no_git)
                all.convert_all(
                    configuration,
                    delete_option,
                    no_git,
                    stop_share,
                    meta_update,
                    vault_share,
                )
        else:
            setup.git_pull(configuration, no_git)
            all.convert_all(configuration, False, no_git, stop_share, meta_update, 0)


if __name__ == "__main__":
    main()
