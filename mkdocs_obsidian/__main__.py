import argparse
import os
import sys
from datetime import datetime
from rich.markdown import Markdown
from rich.console import Console
from rich import print
from pathlib import Path

try:
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

from mkdocs_obsidian.common import (
    config as setup,
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


def obsidian_shell(file="0", meta_update=0, vault_share=0, git=True):
    """
    :param file: Filepath. 0 for all shared files
    :param meta_update: Disable-enable metadata update in source file
    :param vault_share: Share all vault.
    :param git: If true, push to git
    :return: /
    """

    if file == "0":
        all.obsidian_simple(False, git, 1, 0, vault_share)
    elif not os.path.exists(Path(file)):
        file = search_shortcuts(file)
        if not file:
            print("File not found.")
            sys.exit()
        one.convert_one(file, git, meta_update)
    elif file != "0" and os.path.exists(Path(file)):
        one.convert_one(file, git, meta_update)
    sys.exit()


def mobile_shortcuts(file="0", meta_update=0, vault_share=0):
    """
    Main function using on mobile
    :param meta_update: Enable the metadata update
    :param file: File to convert
    :param vault_share: int (bool)
    :return: None
    """
    if file == "0":
        all.convert_all(False, False, 1, 0, vault_share)
    elif not os.path.exists(Path(file)):
        file = search_shortcuts(file)
        if not file:
            print("[u red]File not found.")
            sys.exit()
        one.convert_one(file, False, meta_update)
    elif file == "--c":
        setup.create_env()
        sys.exit()
    elif file != "0" and os.path.exists(Path(file)):
        one.convert_one(file, False, meta_update)


def main():
    """
    Main function using in CLI
    :return: None
    """
    parser = argparse.ArgumentParser(
        description=(
            "Create file in docs and relative folder, move image in assets, convert"
            " admonition code_blocks, add links and push."
        )
    )
    group_files = parser.add_mutually_exclusive_group()
    group_git = parser.add_mutually_exclusive_group()
    group_git.add_argument(
        "--git", "--g", "--G", help="No commit and no push to git", action="store_false"
    )
    group_git.add_argument(
        "--mobile",
        "--shortcuts",
        "--s",
        "--S",
        help="Use mobile shortcuts fonction without push.",
        action="store_true",
    )
    parser.add_argument(
        "--meta",
        "--m",
        "--M",
        help="Update the frontmatter with link",
        action="store_true",
    )
    parser.add_argument(
        "--keep",
        "--k",
        "--K",
        help="Keep deleted file from vault and removed shared file",
        action="store_true",
    )
    parser.add_argument(
        "--config", "--c", "--C", help="Edit the config file", action="store_true"
    )
    parser.add_argument("--obsidian", help=argparse.SUPPRESS, action="store_true")
    parser.add_argument(
        "--force",
        "--d",
        "--D",
        help="Force conversion - only work if path not specified",
        action="store_true",
    )
    group_files.add_argument(
        "--filepath",
        "--f",
        help="Filepath of the file you want to convert",
        action="store",
        required=False,
    )
    group_files.add_argument(
        "--ignore",
        "--ignore-share",
        "--no-share",
        "--i",
        "--vault",
        help="Convert the entire vault without relying on share state.",
        action="store_true",
    )
    console = Console()
    args = parser.parse_args()
    if args.config:
        setup.create_env()
        sys.exit()
    ori = args.filepath
    meta_update = 1
    if args.meta:
        meta_update = 0
    delopt = False
    if args.force:
        delopt = True
    ng = args.git
    share_vault = 0
    if args.ignore:
        share_vault = 1
    if not args.keep:
        info = check.delete_not_exist()
        if len(info) > 1:
            info[0] = "- " + info[0]
            info_str = "\n- ".join(info)
            if args.obsidian:
                console.print(
                    f'[[i not bold sky_blue2]{datetime.now().strftime("%H:%M:%S")}[/]] 🗑️[u'
                    " red bold]Delete from blog :[/]",
                    Markdown(info_str),
                    end="",
                )
            else:
                print(f'[{datetime.now().strftime("%H:%M:%Sf")}] 🗑️ Delete from blog: {info_str}')
        elif len(info) == 1:
            info_str = info[0]
            if args.obsidian:
                console.print(
                    f"🗑️ [u red bold] Delete[/] [bold red i] {info_str}[/] [u red bold]from"
                    " blog[/]"
                )
            else:
                print(f'Delete {info_str} from blog.')
        stop_share = 1
    else:
        stop_share = 0
    if ori:
        if args.obsidian:
            obsidian_shell(ori, meta_update, share_vault, ng)
            sys.exit()
        elif args.mobile:
            mobile_shortcuts(ori, meta_update, share_vault)
            sys.exit()
        elif os.path.exists(Path(ori)):  # Share ONE
            one.convert_one(ori, ng, meta_update)
        else:
            print(f"[red bold]Error :[/] [u]{ori}[/] [red bold]doesn't exist.")
            sys.exit()
    else:
        if args.mobile:
            mobile_shortcuts("0", meta_update, share_vault)
            sys.exit()
        elif args.obsidian:
            obsidian_shell("0", meta_update, share_vault)
            sys.exit()
        all.convert_all(delopt, ng, stop_share, meta_update, share_vault)


if __name__ == "__main__":
    main()
