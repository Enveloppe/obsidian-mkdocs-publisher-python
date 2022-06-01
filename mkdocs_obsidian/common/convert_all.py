"""
Convert all file in a vault folder.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

import frontmatter
import yaml
from rich import print
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import track
from rich.rule import Rule

from mkdocs_obsidian.common import config, conversion as convert, file_checking as check, github_push as gitt


def dest(filepath: Path, folder: Path) -> str:
    """
    Returns the final destination path of the file.
    """
    file_name = os.path.basename(filepath)
    destination = Path(folder, file_name)
    return str(destination)


def search_share(
    configuration: config.Configuration,
    preserve=0,
    stop_share=1,
    meta=0,
    vault_share=0,
    obsidian=False,
) -> tuple[list[str], str]:
    """Search file to publish, convert and write them."""

    DEFAULT_NOTES = configuration.default_folder
    VAULT_FILE = configuration.vault_file
    SHARE = configuration.share_key
    CATEGORY = configuration.category_key
    filespush = []
    check_file = False
    clipkey = DEFAULT_NOTES
    description = "[cyan u]Scanning\n"
    for filepath in track(
        VAULT_FILE, description=description, total=len(VAULT_FILE), disable=obsidian
    ):
        if (
            filepath.endswith(".md")
            and "excalidraw" not in filepath
            and not check.exclude(filepath, "folder", configuration.output)
        ):
            try:
                yaml_front = frontmatter.load(filepath)
                clipkey = yaml_front.get(CATEGORY, DEFAULT_NOTES)
                if not clipkey:
                    clipkey = "hidden"
                if yaml_front.get(SHARE) or vault_share == 1:
                    folder = check.create_folder(clipkey, configuration, 0)
                    if preserve == 0:  # preserve
                        if yaml_front.get("update") is False:
                            update = 1
                        else:
                            update = 0

                        if check.skip_update(
                            Path(filepath), folder, update
                        ) or not check.modification_time(Path(filepath), folder, update):
                            check_file = False
                        else:
                            contents = convert.file_convert(
                                configuration, filepath, vault_share
                            )
                            if check.diff_file(Path(filepath), folder, contents, update):
                                check_file = convert.file_write(
                                    configuration, filepath, contents, folder, meta
                                )
                            else:
                                check_file = False
                    elif preserve == 1:  # force deletions
                        contents = convert.file_convert(
                            configuration, filepath, vault_share
                        )
                        check_file = convert.file_write(
                            configuration, filepath, contents, folder, meta
                        )
                    msg_folder = os.path.basename(folder)
                    destination = dest(Path(filepath), folder)
                    if check_file:
                        filespush.append(
                            "Added :"
                            f" {os.path.basename(destination).replace('.md', '')} in"
                            f" [{msg_folder}]"
                        )
                elif stop_share == 1:
                    folder = check.create_folder(clipkey, configuration, 1)
                    file_name = os.path.basename(filepath).replace(".md", "")
                    if file_name == os.path.basename(folder):
                        filepath = filepath.replace(file_name, "index")
                    if check.delete_file(Path(filepath), folder, configuration, meta):
                        msg_folder = os.path.basename(folder)
                        destination = dest(Path(filepath), folder)
                        filespush.append(
                            "Removed :"
                            f" {os.path.basename(destination).replace('.md', '')} from"
                            f" [{msg_folder}]"
                        )
            except yaml.YAMLError:
                print(f"Skip [u bold red]{filepath}[/] because of YAML error.\n")
            except Exception as e:
                print(
                    f"Skip [u bold red]{filepath}[/] because of an unexpected error :"
                    f" {e}\n"
                )
    return filespush, clipkey


def obsidian_simple(
    configuration: config.Configuration,
    delopt=False,
    git=True,
    stop_share=0,
    meta=0,
    vault_share=0,
):
    """
    Convert file without markup for obsidian shell command.
    """
    if not git:
        git_info = "No push"
    else:
        git_info = "Push"
    time_now = datetime.now().strftime("%H:%M:%S")
    msg_info = ""
    if vault_share == 1:
        msg_info = "\n- Share entire vault [ignore share]"
    if delopt:  # preservesdds
        print(
            f"[{time_now}] STARTING CONVERT ALL\n\n- {git_info}\n- Force"
            f" deletion{msg_info}"
        )
        new_files, clipkey = search_share(
            configuration, 1, stop_share, meta, vault_share, obsidian=True
        )
    else:
        print(f"[{time_now}] STARTING CONVERT ALL\n- {git_info}\n{msg_info}")
        new_files, clipkey = search_share(
            configuration, 0, stop_share, meta, vault_share, obsidian=True
        )
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
            remove_info = "🗑 Removed from blog : "
        if len(add_msg) > 0:
            add_info = "🎉 Added to blog :"
        commit = add_msg + remove_msg
        if git:
            if len(new_files) == 1:
                commit = "".join(new_files)
                markdown_msg = commit[commit.find(":") + 2 : commit.rfind("in") - 1]
                convert.clipboard(configuration, markdown_msg, clipkey)
            commit = f"Updated :\n\n {commit}\n"
            gitt.git_push(
                commit,
                configuration,
                True,
                add_info=add_info,
                rmv_info=remove_info,
                add_msg=add_msg,
                remove_msg=remove_msg,
            )
        else:
            print(
                f"[{datetime.now().strftime('%H:%M:%S')}]"
                f"{add_info}: {add_msg}\n{remove_info}: {remove_msg}"
            )
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] No modification 😶")
    sys.exit()


def convert_all(
    configuration: config.Configuration,
    delopt: bool = False,
    git: bool = True,
    stop_share: int = 0,
    meta: int = 0,
    vault_share: int = 0,
):
    """Convert all shared file with relying on rich markup library."""
    console = Console()
    if not git:
        git_info = "No push"
    else:
        git_info = "Push"
    time_now = datetime.now().strftime("%H:%M:%S")
    msg_info = ""
    if vault_share == 1:
        msg_info = "\n- Share entire vault [**ignore share**]"
    if delopt:
        console.print(
            Rule(
                f"[[i not bold sky_blue2]{time_now}[/]] [deep_sky_blue3 bold]STARTING"
                " CONVERT[/] [[i sky_blue2]ALL[/]]",
                align="center",
                end="",
                style="deep_sky_blue3",
            ),
            Markdown(f"- {git_info}\n- Force deletion{msg_info}", justify="full"),
            end=" ",
            new_line_start=True,
            justify="full",
        )
        new_files, clipkey = search_share(
            configuration, 1, stop_share, meta, vault_share
        )
    else:
        console.print(
            Rule(
                f"[[i not bold sky_blue2]{time_now}[/]] [deep_sky_blue3 bold]STARTING"
                " CONVERT[/] [[i sky_blue2]ALL[/]]",
                align="center",
                end="",
                style="deep_sky_blue3",
            ),
            Markdown(f"- {git_info}\n{msg_info}"),
            " ",
            new_line_start=True,
        )
        new_files, clipkey = search_share(
            configuration, 0, stop_share, meta, vault_share
        )
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
        if git:
            if len(new_files) == 1:
                commit = "".join(new_files)
                markdown_msg = commit[commit.find(":") + 2 : commit.rfind("in") - 1]
                convert.clipboard(configuration, markdown_msg, clipkey)
            commit = f"**Updated** : \n {commit}\n"
            gitt.git_push(
                commit,
                configuration,
                add_info=add_info,
                rmv_info=remove_info,
                add_msg=add_msg,
                remove_msg=remove_msg,
            )
        else:
            console.print(
                f"[[i not bold sky_blue2]{datetime.now().strftime('%H:%M:%S')}[/]]"
                f" {add_info}",
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
