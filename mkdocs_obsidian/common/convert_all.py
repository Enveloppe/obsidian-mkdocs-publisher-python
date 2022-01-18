"""
Convert all file in a vault folder.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

import frontmatter
import yaml
from rich.progress import track
from rich.rule import Rule
from rich.markdown import Markdown
from rich.console import Console
from rich import print
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


def exclude_folder(filepath: str):
    """
    Check if the file is in an excluded folder
    :param filepath: file to check
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


def dest(filepath: str, folder: str):
    """
    Return the path of the final file
    :param filepath: file to convert
    :param folder: final folder
    :return: str
    """
    file_name = os.path.basename(filepath)
    destination = Path(f"{folder}/{file_name}")
    return str(destination)


def search_share(preserve=0, stop_share=1, meta=0, vault_share=0):
    """
    Search file to publish
    :param preserve: if 1 force update
    :param stop_share: remove stoped shared file if 1
    :param meta: Update the metadata if 1
    :param vault_share: If all the vault need to be shared
    :return: Contents of the notes
    """
    filespush = []
    check_file = False
    clipkey = "notes"
    description = "[cyan u]Scanning\n"
    for filepath in track(VAULT_FILE, description=description, total=len(VAULT_FILE)):
        if (
            filepath.endswith(".md")
            and "excalidraw" not in filepath
            and not exclude_folder(filepath)
        ):
            try:
                yaml_front = frontmatter.load(filepath)
                clipkey = yaml_front.get("category", "notes")
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
                print(f"Skip [u bold red]{filepath}[/] because of YAML error.\n")
            except Exception as e:
                print(
                    f"Skip [u bold red]{filepath}[/] because of an unexpected error : {e}\n"
                )
    return filespush, clipkey


def convert_all(delopt=False, git=False, stop_share=0, meta=0, vault_share=0):
    """
    Main function to convert multiple file
    :param delopt: Force deletion if True
    :param git: Git push if True
    :param stop_share: Delete stoped shared file if 0
    :param meta: Update frontmatter if 1
    :param vault_share: Share all file in vault if 1
    :return: None
    """
    console = Console()
    if git:
        git_info = "No push"
    else:
        git_info = "Push"
    time_now = datetime.now().strftime("%H:%M:%S")
    msg_info = ""
    if vault_share == 1:
        msg_info = "\n- Share entire vault [**ignore share**]"
    if delopt:  # preserve
        console.print(
            Rule(
                f"[[i not bold sky_blue2]{time_now}[/]] [deep_sky_blue3 bold]STARTING CONVERT[/] [[i sky_blue2]ALL[/]]",
                align="center",
                end="",
                style="deep_sky_blue3",
            ),
            Markdown(f"- {git_info}\n- Force deletion{msg_info}", justify="full"),
            end=" ",
            new_line_start=True,
            justify="full",
        )
        new_files, clipkey = search_share(1, stop_share, meta, vault_share)
    else:
        console.print(
            Rule(
                f"[[i not bold sky_blue2]{time_now}[/]] [deep_sky_blue3 bold]STARTING CONVERT[/] [[i sky_blue2]ALL[/]]",
                align="center",
                end="",
                style="deep_sky_blue3",
            ),
            Markdown(f"- {git_info}\n{msg_info}"),
            " ",
            new_line_start=True,
        )
        new_files, clipkey = search_share(0, stop_share, meta, vault_share)
    if len(new_files) > 0:
        add_msg = ""
        remove_msg = ""
        for markdown_msg in new_files:
            if "removed" in markdown_msg.lower():
                remove_msg = (
                    remove_msg + "\n- " + markdown_msg.replace("Removed : ", "")
                )
            elif "added" in markdown_msg.lower():
                add_msg = add_msg + "\n- " + markdown_msg.replace("Added : ", "")
        remove_info = ""
        add_info = ""
        if len(remove_msg) > 0:
            remove_info = "🗑 [u bold red]Removed from blog : "
        if len(add_msg) > 0:
            add_info = "🎉 [u bold sky_blue2]Added to blog :"
        commit = add_msg + remove_msg
        if git is False:
            if len(new_files) == 1:
                commit = "".join(new_files)
                markdown_msg = commit[commit.find(":") + 2 : commit.rfind("in") - 1]
                convert.clipboard(markdown_msg, clipkey)
            commit = f"**Updated** : \n {commit}"
            config.git_push(commit)
        else:
            console.print(
                f"[[i not bold sky_blue2]{datetime.now().strftime('%H:%M:%S')}[/]] {add_info}",
                Markdown(add_msg),
                remove_info,
                Markdown(remove_msg),
                end=" ",
            )
    else:
        console.print(
            f"[[i not bold sky_blue2]{datetime.now().strftime('%H:%M:%S')}[/]]",
            Markdown("*No modification 😶*"),
            end=" ",
        )
    sys.exit()
