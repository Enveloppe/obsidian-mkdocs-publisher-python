"""
Convert all file in a vault folder.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

import frontmatter
import yaml

from mkdocs_obsidian.common import (
    config,
    global_value as gl,
    file_checking as check,
    conversion as convert,
)

BASEDIR = gl.BASEDIR
VAULT = gl.VAULT
VAULT_FILE = gl.VAULT_FILE
SHARE = gl.SHARE


def exclude_folder(filepath):
    """
    Check if the file is in an excluded folder
    :param filepath: str
    :return: boolean
    """
    config_folder = Path(f"{BASEDIR}/exclude_folder.yml")
    if os.path.exists(config_folder):
        with open(config_folder, "r", encoding="utf-8") as file_config:
            try:
                folder = yaml.safe_load(file_config)
            except yaml.YAMLError as exc:
                print(exc)
                sys.exit(1)
        return any(str(Path(file)) in filepath for file in folder)
    return False


def dest(filepath, folder):
    """
    Return the path of the final file
    :param filepath: str
    :param folder: str
    :return: str
    """
    file_name = os.path.basename(filepath)
    destination = Path(f"{folder}/{file_name}")
    return str(destination)


def search_share(preserve=0, stop_share=1, meta=0, vault_share=0):
    """
    Search file to publish
    :param preserve: int (bool)
    :param stop_share: int (bool)
    :param meta: int (bool)
    :param vault_share int (bool)
    :return: tuple[list(str), str]
    """
    filespush = []
    check_file = False
    clipkey = "notes"
    for filepath in VAULT_FILE:
        if (
            filepath.endswith(".md")
            and "excalidraw" not in filepath
            and not exclude_folder(filepath)
        ):
            try:
                yaml_front = frontmatter.load(filepath)

                if yaml_front.get("category"):
                    clipkey = yaml_front["category"]
                else:
                    clipkey = "notes"
                if yaml_front.get(SHARE) or vault_share == 1:
                    folder = check.create_folder(clipkey, 0)

                    if preserve == 0:  # preserve
                        if yaml_front.get("update") is False:
                            update = 1
                        else:
                            update = 0

                        if check.skip_update(
                            filepath, folder, update
                        ) or not check.modification_time(filepath, folder, update):
                            check_file = False
                        else:
                            contents = convert.file_convert(filepath, vault_share)
                            if check.diff_file(filepath, folder, contents, update):
                                check_file = convert.file_write(
                                    filepath, contents, folder, meta
                                )
                            else:
                                check_file = False
                    elif preserve == 1:  # force deletions
                        contents = convert.file_convert(filepath, vault_share)
                        check_file = convert.file_write(
                            filepath, contents, folder, meta
                        )
                    msg_folder = os.path.basename(folder)
                    destination = dest(filepath, folder)
                    if check_file:
                        filespush.append(
                            f"Added : {os.path.basename(destination).replace('.md', '')} in [{msg_folder}]"
                        )
                elif stop_share == 1:
                    folder = check.create_folder(clipkey, 1)
                    file_name = os.path.basename(filepath).replace(".md", "")
                    if file_name == os.path.basename(folder):
                        filepath = filepath.replace(file_name, "index")
                    if check.delete_file(filepath, folder, meta):
                        msg_folder = os.path.basename(folder)
                        destination = dest(filepath, folder)
                        filespush.append(
                            f"Removed : {os.path.basename(destination).replace('.md', '')} from [{msg_folder}]"
                        )
            except yaml.YAMLError:
                print(f"Skip {filepath} because of YAML error.\n")
            except Exception as e:
                print(f"Skip {filepath} because of an unexpected error : {e}\n")
    return filespush, clipkey


def convert_all(delopt=False, git=False, stop_share=0, meta=0, vault_share=0):
    """
    Main function to convert multiple file
    :param delopt: bool
    :param git: bool
    :param stop_share: int (bool)
    :param meta: int (bool)
    :param vault_share: int (bool)
    :return: None
    """
    if git:
        git_info = "NO PUSH"
    else:
        git_info = "PUSH"
    time_now = datetime.now().strftime("%H:%M:%S")
    msg_info = "\n"
    if vault_share == 1:
        msg_info = "\n- SHARE ENTIRE VAULT [IGNORE SHARE STATE]\n"
    if delopt:  # preserve
        print(
            f"[{time_now}] STARTING CONVERT [ALL] OPTIONS :\n- {git_info}\n- FORCE DELETIONS{msg_info}"
        )
        new_files, clipkey = search_share(1, stop_share, meta, vault_share)
    else:
        print(f"[{time_now}] STARTING CONVERT [ALL] OPTIONS :\n- {git_info}{msg_info}")
        new_files, clipkey = search_share(0, stop_share, meta, vault_share)
    if len(new_files) > 0:
        add_msg = ""
        remove_msg = ""
        for markdown_msg in new_files:
            if "removed" in markdown_msg.lower():
                remove_msg = (
                    remove_msg + "\n - " + markdown_msg.replace("Removed : ", "")
                )
            elif "added" in markdown_msg.lower():
                add_msg = add_msg + "\n - " + markdown_msg.replace("Added : ", "")

        if len(remove_msg) > 0:
            remove_msg = f"🗑️ Removed from blog : {remove_msg}"
        if len(add_msg) > 0:
            add_msg = f" 🎉 Added to blog : {add_msg}\n\n"
        commit = add_msg + remove_msg
        if git is False:
            if len(new_files) == 1:
                commit = "".join(new_files)
                markdown_msg = commit[commit.find(":") + 2 : commit.rfind("in") - 1]
                convert.clipboard(markdown_msg, clipkey)
            commit = f"Updated : \n {commit}"
            config.git_push(commit)
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {commit}")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] No modification 😶")
    sys.exit()
