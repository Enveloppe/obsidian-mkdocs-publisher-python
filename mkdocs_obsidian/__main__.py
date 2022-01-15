import argparse
import os
import sys
from datetime import datetime


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
    for md in value.vault_file:
        if os.path.basename(md) == os.path.basename(file):
            return md
    return False


def mobile_shortcuts(file="0", meta_update=0, vault_share=0):
    """
    Main function using on mobile
    :param meta_update: int (bool)
    :param file: String (file path)
    :param vault_share: int (bool)
    :return: None
    """
    if file == "0":
        all.convert_all(False, False, 0, 0, vault_share)
    elif not os.path.exists(file):
        file = search_shortcuts(file)
        if not file:
            print("File not found.")
            sys.exit()
        one.convert_one(file, True, meta_update)
    elif file == "--c":
        setup.create_env()
        sys.exit()
    elif file != "0" and os.path.exists(file):
        one.convert_one(file, True, meta_update)


def main():
    """
    Main function using in CLI
    :return: None
    """
    parser = argparse.ArgumentParser(
        description="Create file in docs and relative folder, move image in assets, convert admonition code_blocks, add links and push."
    )
    group_files = parser.add_mutually_exclusive_group()
    group_git = parser.add_mutually_exclusive_group()
    group_git.add_argument(
        "--git", "--g", "--G", help="No commit and no push to git", action="store_true"
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
            print(
                f'[{datetime.now().strftime("%H:%M:%S")}] 🗑️ Delete from blog:\n{info_str}'
            )
        elif len(info) == 1:
            info_str = info[0]
            print(f'🗑️ Delete "{info_str}" from blog')
        stop_share = 1
    else:
        stop_share = 0
    if ori:
        if args.mobile:
            mobile_shortcuts(ori, meta_update)
            sys.exit()
        elif os.path.exists(ori):  # Share ONE
            one.convert_one(ori, ng, meta_update)
        else:
            print(f"Error : {ori} doesn't exist.")
            sys.exit()
    else:
        if args.mobile:
            mobile_shortcuts("0", meta_update)
            sys.exit()
        all.convert_all(delopt, ng, stop_share, meta_update, share_vault)


if __name__ == "__main__":
    main()
