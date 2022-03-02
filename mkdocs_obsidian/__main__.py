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
    global_value as value,
    convert_all as all,
    convert_one as one,
    file_checking as check,
)


def search_shortcuts(file):
    """
    Search a specific file in vault, using shortcuts on IOS
    :param file: str (filepath)
    :return: str (filepath) / False
    """
    if not file.endswith(".md"):
        file = file + ".md"
    for md in value.VAULT_FILE:
        if os.path.basename(md) == os.path.basename(file):
            return md
    return False


def obsidian_shell(file="0", meta_update=0, vault_share=0, git=True, delete_option=False):
    """
    """

    if file == "0":
        all.obsidian_simple(delete_option, git, 1, 0, vault_share)
    elif not os.path.exists(Path(file)):
        file = search_shortcuts(file)
        if not file:
            print("File not found.")
            sys.exit(1)
        one.convert_one(file, git, meta_update)
    elif file != "0" and os.path.exists(Path(file)):
        one.convert_one(file, git, meta_update)
    sys.exit()


def mobile_shortcuts(file="0", meta_update=0, vault_share=0, delete_option=False):
    """

    """
    from mkdocs_obsidian.common import config as setup

    if file == "0":
        all.convert_all(delete_option, False, 1, 0, vault_share)
    elif not os.path.exists(Path(file)):
        file = search_shortcuts(file)
        if not file:
            print("[u red]File not found.")
            sys.exit(1)
        one.convert_one(file, False, meta_update)
    elif file == "--c":
        setup.create_env()
    elif file != "0" and os.path.exists(Path(file)):
        one.convert_one(file, False, meta_update)

def keep(obsidian, console):
    info = check.delete_not_exist()
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
        - publish : Share all vault
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
        - `--git` : No commit and push to git ;
        - `--mobile` : Use mobile shortcuts instead of `--git`
        - `--meta` : Update frontmatter of source files
        - `--keep` : Don't delete files in blog folder
        - `--shell` : Remove Rich printing
    Commands and specific options : 
        - configuration :
            - `--new configuration_name` : Create a specific configuration for some files
        - publish : Share all vault
            - `--force` : Force updating
            - `--vault` : Share all vault file, ignoring the share state.
        - `file [file*]` : Share only one file
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
        '--vault', action="store_true", help="Publish all file in your vault, ignoring the share state. "
        )

    files_cmd = subparser.add_parser("file", help="Publish only one file")
    files_cmd.add_argument("filepath", action="store")
    group_git = parser.add_mutually_exclusive_group()
    group_git.add_argument(
        "--mobile",
        "--shortcuts",
        help="Use mobile shortcuts, without push",
        action="store_true"
        )
    group_git.add_argument("--git", "--g", '--G', help="No commit and no push to git", action="store_false")

    parser.add_argument('--meta', '--m', '--M', help='Update the frontmatter of the source file with the link to the note', action="store_false")
    parser.add_argument(
        "--keep",
        "--k",
        "--K",
        help="Keep deleted file from vault and removed shared file",
        action="store_true",
        )
    parser.add_argument("--obsidian", "--shell", help=argparse.SUPPRESS, action='store_true')
    console = Console()
    args = parser.parse_args()
    meta_update = int(args.meta)
    no_git = args.git
    if not args.keep:
        stop_share = (args.obsidian, console)
    else:
        stop_share = 0
    cmd = args.cmd
    if cmd == 'config':
        from mkdocs_obsidian.common import config as setup

        setup.create_env()
        sys.exit()
    #meta-update

    elif cmd == "file":
        file_source = args.filepath
        if args.obsidian:
            obsidian_shell(file_source,meta_update, git=no_git)
            sys.exit()
        elif args.mobile:
            mobile_shortcuts(file_source, meta_update)
            sys.exit()
        elif os.path.exists(Path(file_source)):
            one.convert_one(file_source, no_git, meta_update)
        else:
            print(f"[red bold]Error :[/] [u]{file_source}[/] [red bold]doesn't exist.")
            sys.exit(1)

    elif cmd=="all":
        vault_share = int(args.vault)
        delete_option = args.force
        if args.mobile:
            mobile_shortcuts("0", meta_update, vault_share, delete_option)
        elif args.obsidian:
            obsidian_shell("0", meta_update, vault_share, delete_option)
        else:
            all.convert_all(delete_option, no_git, stop_share, meta_update, vault_share)
if __name__ == "__main__":
    main()
