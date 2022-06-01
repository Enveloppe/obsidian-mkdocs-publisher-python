"""
All function intended to check the file and their path.
"""

import glob
import json
import os
import sys
from pathlib import Path, PurePath

import frontmatter
import yaml
from unidecode import unidecode

from mkdocs_obsidian.common import metadata as mt, config as cfg


def config_exclude(BASEDIR: Path) -> Path:
    """
    A simple script to add compatibility with older version : the renaming of .exclude_folder to .exclude
    """
    config_folder = Path(BASEDIR, "exclude_folder.yml")
    if not os.path.exists(config_folder):
        config_folder = Path(BASEDIR, "exclude.yml")
    return config_folder


def exclude(filepath: str, key: str, BASEDIR: Path) -> bool:
    """
    Check if a file is in `exclude.yml`.
    """
    config_folder = config_exclude(BASEDIR)
    if os.path.exists(config_folder):
        with open(config_folder, "r", encoding="utf-8") as file_config:
            try:
                folder = yaml.safe_load(file_config)
            except yaml.YAMLError as exc:
                print(f"[red bold]Error in [u]{filepath}[/] : {exc}")
                sys.exit(2)
        excluded_folder = folder.get(key, "")
        return any(str(Path(file)) in filepath for file in excluded_folder)
    return False


def move_file_by_category(
    filepath: Path, clipkey: str, configuration: cfg.Configuration
) -> bool:
    glog_folder = Path(configuration.output, "docs", "**")
    blog_file = [
        file
        for file in glob.glob(str(glog_folder), recursive=True)
        if os.path.isfile(file)
    ]
    file_name = os.path.basename(filepath)
    if file_name == "index.md":
        file_name = PurePath(clipkey).name + ".md"
    old_file = [file for file in blog_file if os.path.basename(file) == file_name]
    if old_file:
        old_file = old_file[0]
        with open(old_file, "r", encoding="utf-8") as file:
            meta_data = frontmatter.loads(file.read())
        category = meta_data.get(configuration.category_key, "")
        if category != clipkey:
            os.remove(Path(old_file))
            return True
    return False


def delete_old_index(index_path: Path, configuration: cfg.Configuration) -> str:
    with open(index_path, "r", encoding="utf-8") as file:
        meta_data = frontmatter.loads(file.read())
    old_category = meta_data.get(configuration.category_key, "")
    name = PurePath(old_category).name + ".md"
    in_vault = [x for x in configuration.vault_file if os.path.basename(x) == name]
    if in_vault:
        with open(in_vault[0], "r", encoding="utf-8") as file:
            meta_data = frontmatter.loads(file.read())
        category = meta_data.get(configuration.category_key, "")
        share = meta_data.get(configuration.share_key, "False")
        if category != old_category and share is True:
            try:
                os.remove(index_path)
                folder = os.path.dirname(index_path)
                if len(os.listdir(folder)) == 0 and os.path.basename(folder) != "docs":
                    # Delete folder
                    os.rmdir(folder)
                return name.replace(".md", "") + "/" + "index.md"
            except PermissionError:
                return ""
            except IsADirectoryError:
                return ""
    return ""


def delete_not_exist(configuration: cfg.Configuration, actions=False) -> list[str]:
    """
    Removes files that have been deleted from the vault unless they are in `exclude.yml[files]` and always delete if
    founded file is in `exclude.yml[folder]`
    """
    BASEDIR = configuration.output
    VAULT_FILE = configuration.vault_file
    vault_file = []
    info = []
    excluded = []
    important_folder = ["assets", "css", "js", "logo", "script"]
    docs = Path(f"{BASEDIR}/docs/**")
    if actions and actions != "minimal":
        if os.path.isfile(Path(os.getcwd(), "source", "vault_published.json")):
            with open(
                Path(os.getcwd(), "source", "vault_published.json"),
                "r",
                encoding="utf-8",
            ) as file:
                VAULT_FILE = json.load(file)
                vault_file = []
            if len(VAULT_FILE) == 0:
                return []
        elif os.path.exists(Path(os.getcwd(), "source", "vault_published.txt")):
            vault_file = ""
            with open(
                Path(os.getcwd(), "source", "vault_published.txt"),
                "r",
                encoding="utf-8",
            ) as file_vault:
                vault_file = vault_file + file_vault.read()
            vault_file = (
                vault_file.replace("\n", " ")
                .replace("]", "")
                .replace("[", "")
                .replace('"', "")
                .replace("'", "")
                .split(",")
            )
            VAULT_FILE = vault_file
            vault_file = []
            if len(VAULT_FILE) == 0:
                return []
        else:
            return []
    for note in VAULT_FILE:
        vault_file.append(os.path.basename(note))
        if exclude(note, "folder", BASEDIR):
            excluded.append(os.path.basename(note))
    for file in glob.iglob(str(docs), recursive=True):
        if os.path.basename(file) == "index.md":
            index = delete_old_index(Path(file), configuration)
            if len(index) != 0:
                info.append(index)
        elif (
            not any(i in file for i in important_folder)
            and not exclude(file, "files", BASEDIR)
            and (
                os.path.basename(file) not in vault_file
                or os.path.basename(file) in excluded
            )
        ):
            try:
                if os.path.isfile(Path(file)):
                    file = Path(file)
                    os.remove(file)
                    folder = os.path.dirname(file)
                    if (
                        len(os.listdir(folder)) == 0
                        and os.path.basename(folder) != "docs"
                    ):
                        # Delete folder
                        os.rmdir(folder)
                    info.append(folder)
            except PermissionError:
                pass
            except IsADirectoryError:
                pass
    return info


def diff_file(filepath: Path, folder: Path, contents: list[str], update=0) -> bool:
    """Check the difference between file in vault and file in publish.
    Check if the new converted file = the file on publish.
    """
    filename = os.path.basename(filepath)
    shortname = unidecode(os.path.splitext(filename)[0])
    foldername = unidecode(folder.name)
    if check_file(filename, folder) == "EXIST":
        if update == 1:
            return False
        if foldername == shortname:
            filename = "index.md"
        note = Path(folder, filename)
        retro_old = retro(note)
        meta_old = frontmatter.load(note)
        meta_old = meta_old.metadata
        meta_old.pop("link", None)
        try:
            front_temp = frontmatter.loads("".join(contents))
        except yaml.YAMLError:
            print(f"Skip {filepath} : YAML Error")
            return False  # skip
        new_version = retro(contents, 1)
        meta_new = front_temp.metadata
        meta_new.pop("link", None)
        if (
            new_version == retro_old
            and sorted(meta_old.keys()) == sorted(meta_new.keys())
            and sorted(str(meta_old.values())) == sorted(str(meta_new.values()))
        ):
            return False
        return True
    return True  # Si le fichier existe pas, il peut pas être identique


def retro(file: Path | list, opt=0) -> list[str]:
    """Remove metadata from note"""
    notes = []
    if opt == 0:
        try:
            metadata = frontmatter.load(file)
        except yaml.YAMLError:
            os.remove(file)
            return notes
    else:
        metadata = frontmatter.loads("".join(file))
    file = metadata.content.split("\n")
    for line in file:
        notes.append(line)
    return notes


def create_folder(category: str, configuration: cfg.Configuration, share=0) -> Path:
    """
    create a folder based on the category key as 'folder1/folder2/.../' and return the folder path. Return default
    path in case of error/none category
    """
    BASEDIR = configuration.output
    POST = configuration.post

    if category != "":
        folder = Path(BASEDIR, 'docs', category)
        try:
            if share == 0:
                folder.mkdir(parents=True, exist_ok=True)
        except OSError:
            folder = Path(POST)
    else:
        folder = Path(POST)
    return folder


def modification_time(filepath: Path, folder: Path, update: int) -> bool:
    """check the modification time : return true if file modified since the last push."""
    if update == 0:
        return True  # Force update
    filename = os.path.basename(filepath)
    note = Path(folder, filename)
    if os.path.isfile(note):
        return filepath.stat().st_mtime > note.stat().st_mtime
    return True  # file doesn't exist


def skip_update(filepath: Path, folder: Path, update: int) -> bool:
    """check if file exist + update is false"""
    return update == 1 and check_file(filepath, folder) == "EXIST"


def check_file(filepath: Path, folder: Path) -> str:
    """check if the requested file exist or not in publish."""
    file = os.path.basename(filepath)
    shortname = unidecode(os.path.splitext(file)[0])
    foldername = unidecode(folder.name)
    if foldername == shortname:
        file = "index.md"
    publish = Path(folder, file)
    if os.path.isfile(publish):
        return "EXIST"
    return "NE"


def delete_file(
    filepath: Path, folder: Path, configuration: cfg.Configuration, meta_update=1
) -> bool:
    """Delete the requested file"""
    try:
        for file in os.listdir(str(folder)): #prevent bytes error
            filename = unidecode(os.path.basename(filepath))
            filecheck = unidecode(os.path.basename(str(file)))
            if filecheck == filename:
                os.remove(Path(folder, file))
                if meta_update == 0:
                    mt.update_frontmatter(filepath, configuration, 0)
                return True
        if len(os.listdir(folder)) == 0:
            os.rmdir(folder)
    except FileNotFoundError:
        pass
    return False
