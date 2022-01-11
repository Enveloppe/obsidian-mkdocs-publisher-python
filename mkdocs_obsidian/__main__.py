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
    for md in setup.vault_file:
        if os.path.basename(md) == os.path.basename(file):
            return md
    return False


def mobile_shortcuts(shortcuts=False, file="0"):
    """
    Main function using on mobile
    :param shortcuts: bool (default: False)
    :param file: String (file path)
    :return: None
    """
    delopt = False
    git = True
    if shortcuts and (file != "0" or file != "--c"):
        file = search_shortcuts(file)
        if not file:
            print("File not found.")
            sys.exit(1)
        one.convert_one(file, delopt, git)
    elif file == "--c":
        setup.create_env()
    elif file != "0" and os.path.exists(file):
        one.convert_one(file, delopt, git)
    else:
        all.convert_all(git=False)


def main():
    """
    Main function using in CLI
    :return: None
    """
    parser = argparse.ArgumentParser(
        description="Create file in docs and relative folder, move image in assets, convert admonition code_blocks, add links and push."
    )
    group_f = parser.add_mutually_exclusive_group()
    parser.add_argument(
        "--git", "--g", "--G", help="No commit and no push to git", action="store_true"
    )
    parser.add_argument(
        "--mobile", "--shortcuts", "--s", "--S", help="Use mobile shortcuts fonction.", action="store_true"
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
    group_f.add_argument(
        "--force",
        "--d",
        "--D",
        help="Force conversion - only work if path not specified",
        action="store_true",
    )
    group_f.add_argument(
        "--filepath",
        "--f",
        help="Filepath of the file you want to convert",
        action="store",
        required=False,
    )
    args = parser.parse_args()
    if args.config:
        setup.create_env()
        sys.exit(1)
    ori = args.filepath
    if args.mobile:
        mobile_shortcuts(True, ori)
        sys.exit(1)
    meta_update = 1
    if args.meta:
        meta_update = 0
    delopt = False
    if args.force:
        delopt = True
    ng = args.git


    if not args.keep:
        info = check.delete_not_exist()
        if len(info) > 1:
            info_str = "\n -".join(info)
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
        if os.path.exists(ori):  # Share ONE
            one.convert_one(ori, ng, meta_update)
        else:
            print(f"Error : {ori} doesn't exist.")
            return
    else:
        all.convert_all(delopt, ng, stop_share, meta_update)


if __name__ == "__main__":
    main()
