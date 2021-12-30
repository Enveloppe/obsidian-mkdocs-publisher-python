import os
from datetime import datetime
from pathlib import Path

import frontmatter
import yaml

from mkdocs_obsidian.common import config, file_checking as check, conversion as convert

BASEDIR = config.BASEDIR
vault = config.vault


def exclude_folder(filepath):
    config_folder = Path(f"{BASEDIR}/exclude_folder.yml")
    if os.path.exists(config_folder):
        with open(config_folder, "r", encoding="utf-8") as config:
            try:
                folder = yaml.safe_load(config)
            except yaml.YAMLError as exc:
                print(exc)
                exit(1)
        return any(str(Path(file)) in filepath for file in folder)
    return False


def dest(filepath, folder):
    file_name = os.path.basename(filepath)
    dest = Path(f"{folder}/{file_name}")
    return str(dest)


def search_share(option=0, stop_share=1, meta=0):
    filespush = []
    check_file = False
    clipKey = "notes"
    share = config.share
    for sub, dirs, files in os.walk(Path(vault)):
        for file in files:
            filepath = sub + os.sep + file
            if (
                filepath.endswith(".md")
                and "excalidraw" not in filepath
                and not exclude_folder(filepath)
            ):
                try:
                    yaml_front = frontmatter.load(filepath)
                    if "category" in yaml_front.keys():
                        clipKey = yaml_front["category"]
                    if share in yaml_front.keys() and yaml_front[share] is True:
                        folder = check.create_folder(clipKey, 0)
                        if option == 0:  # preserve
                            if (
                                "update" in yaml_front.keys()
                                and yaml_front["update"] is False
                            ):
                                update = 1
                            else:
                                update = 0
                            contents = convert.file_convert(filepath, folder)
                            if check.diff_file(file, folder, contents, update):
                                check_file = convert.file_write(
                                    filepath, contents, folder, meta
                                )
                            else:
                                check_file = False
                        elif option == 1:  # force deletions
                            contents = convert.file_convert(filepath, folder)
                            check_file = convert.file_write(filepath, contents, folder, meta)
                        msg_folder = os.path.basename(folder)
                        destination = dest(filepath, folder)
                        if check_file:
                            filespush.append(
                                f"Added : {os.path.basename(destination).replace('.md', '')} in [{msg_folder}]"
                            )
                    else:
                        if stop_share == 1:
                            folder = check.create_folder(clipKey, 1)
                            if check.delete_file(filepath, folder):
                                msg_folder = os.path.basename(folder)
                                destination = dest(filepath, folder)
                                filespush.append(
                                    f"Removed : {os.path.basename(destination).replace('.md', '')} from [{msg_folder}]"
                                )
                except (
                    yaml.scanner.ScannerError,
                    yaml.constructor.ConstructorError,
                ) as e:
                    pass
    return filespush, clipKey


def convert_all(delopt=False, git=False, stop_share=0, meta=0):
    if git:
        git_info = "NO PUSH"
    else:
        git_info = "PUSH"
    time_now = datetime.now().strftime("%H:%M:%S")
    if delopt:  # preserve
        print(
            f"[{time_now}] STARTING CONVERT [ALL] OPTIONS :\n- {git_info}\n- FORCE DELETIONS"
        )
        new_files, clipKey = search_share(1, stop_share, meta)
    else:
        print(f"[{time_now}] STARTING CONVERT [ALL] OPTIONS :\n- {git_info}\n")
        new_files, clipKey = search_share(0, stop_share, meta)
    if len(new_files) > 0:
        add = ""
        rm = ""
        for md in new_files:
            if "removed" in md.lower():
                rm = rm + "\n - " + md.replace("Removed : ", "")
            elif "added" in md.lower():
                add = add + "\n - " + md.replace("Added : ", "")

        if len(rm) > 0:
            rm = f"🗑️ Removed from blog : {rm}"
        if len(add) > 0:
            add = f" 🎉 Added to blog : {add}\n\n"
        commit = add + rm
        if git is False:
            if len(new_files) == 1:
                commit = "".join(new_files)
                md = commit[commit.find(":") + 2 : commit.rfind("in") - 1]
                convert.clipboard(md, clipKey)
            commit = f"Updated : \n {commit}"
            config.git_push(commit)
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {commit}")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] No modification 😶")
