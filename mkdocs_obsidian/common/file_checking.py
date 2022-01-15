"""
All function intended to check the file and their path.
"""

import datetime
import glob
import os
import re
from pathlib import Path

import frontmatter
import yaml
from unidecode import unidecode

from mkdocs_obsidian.common import global_value as settings
from mkdocs_obsidian.common import convert_all as exclude
from mkdocs_obsidian.common import metadata as mt

BASEDIR = settings.BASEDIR
POST = settings.POST
VAULT = settings.VAULT
VAULT_FILE = settings.VAULT_FILE


def delete_not_exist():
    """
    Removes files that have been deleted from the vault
    :return: A list of deleted files
    """
    vault_file = []
    info = []
    excluded = []
    important_folder = ["assets", "css", "js", "logo", "script"]
    docs = Path(f"{BASEDIR}/docs/**")
    for note in VAULT_FILE:
        vault_file.append(os.path.basename(note))
        if exclude.exclude_folder(note):
            excluded.append(os.path.basename(note))
    for file in glob.iglob(str(docs), recursive=True):
        if not any(i in file for i in important_folder):
            if not re.search("(README|index|CNAME)", os.path.basename(file)) and (
                os.path.basename(file) not in vault_file
                or os.path.basename(file) in excluded
            ):  # or if file in file_excluded
                try:
                    if os.path.isfile(Path(file)):
                        os.remove(Path(file))
                        folder = os.path.dirname(Path(file))
                        if len(os.listdir(folder)) == 0:
                            # Delete folder
                            os.rmdir(folder)
                        info.append(os.path.basename(file))
                except PermissionError:
                    pass
                except IsADirectoryError:
                    pass
    return info


def diff_file(file, folder, contents, update=0):
    """
    Check the difference between file in vault and file in publish.
    Check if the new converted file = the file on publish.
    :param file: str path
    :param folder: str path
    :param contents: list
    :param update: boolean
    :return: boolean
    """
    filename = os.path.basename(file)
    if check_file(filename, folder) == "EXIST":
        if update == 1:
            return False
        if filename.replace(".md", "") == os.path.basename(folder):
            filename = "index.md"
        note = Path(f"{folder}/{filename}")
        retro_old = retro(note)
        meta_old = frontmatter.load(note)
        meta_old = meta_old.metadata
        meta_old.pop("link", None)
        try:
            front_temp = frontmatter.loads("".join(contents))
        except yaml.YAMLError:
            print(f"Skip {file} : YAML Error")
            return False  # skip
        new_version = retro(contents, 1)
        meta_new = front_temp.metadata
        meta_new.pop("link", None)
        if new_version == retro_old and sorted(meta_old.keys()) == sorted(
            meta_new.keys()
        ):
            return False
        else:
            return True
    else:
        return True  # Si le fichier existe pas, il peut pas être identique


def retro(filepath, opt=0):
    """
    Remove metadata from note
    :param filepath: str or list
    :param opt: boolean
    :return: list
    """
    notes = []

    if opt == 0:
        try:
            metadata = frontmatter.load(filepath)
        except yaml.YAMLError:
            os.remove(filepath)
            return notes
    else:
        metadata = frontmatter.loads("".join(filepath))
    file = metadata.content.split("\n")
    for line in file:
        notes.append(line)
    return notes


def create_folder(category, share=0):
    """
    create a folder based on the category key as 'folder1/folder2/.../'
    :param category: string
    :param share: boolean
    :return: folder path
    """
    if category != "":
        folder = Path(f"{BASEDIR}/docs/{category}")
        try:
            if share == 0:
                folder.mkdir(parents=True, exist_ok=True)
        except OSError:
            folder = Path(POST)
    else:
        folder = Path(POST)
    return folder


def modification_time(filepath, folder, update):
    """
    check the modification time : return true if file modified since the last push.
    :param filepath: str
    :param folder: str
    :param update: boolean
    :return: boolean
    """
    if update == 0:
        return True
    filename = os.path.basename(filepath)
    filepath = Path(filepath)
    note = Path(f"{folder}/{filename}")
    if os.path.isfile(note):
        old_time = datetime.datetime.fromtimestamp(note.stat().st_mtime)
        new_time = datetime.datetime.fromtimestamp(filepath.stat().st_mtime)
        if new_time > old_time:
            return True
    return False


def skip_update(filepath, folder, update):
    """
    check if file exist + update is false
    :param filepath: str path
    :param folder: str path
    :param update: boolean
    :return: boolean
    """
    filepath = Path(filepath)
    if update == 1 and check_file(filepath, folder) == "EXIST":
        return True
    return False


def check_file(filepath, folder):
    """
    check if the requested file exist or not in publish.
    :param filepath: str file path
    :param folder: str folder path
    :return: "EXIST" or "NE"
    """
    file = os.path.basename(filepath)
    folder_check = os.path.basename(folder)
    if file.replace(".md", "") == folder_check:
        file = "index.md"
    publish = Path(f"{folder}/{file}")
    if os.path.isfile(publish):
        return "EXIST"
    return "NE"


def delete_file(filepath, folder, meta_update=1):
    """
    Delete the requested file
    :param filepath: str path
    :param folder: str folder
    :param meta_update: boolean
    :return: boolean
    """
    path = Path(folder)
    try:
        for file in os.listdir(path):
            filename = unidecode(os.path.basename(filepath))
            filecheck = unidecode(os.path.basename(file))
            if filecheck == filename:
                os.remove(Path(f"{path}/{file}"))
                if meta_update == 0:
                    mt.update_frontmatter(filepath, 0)
                return True
        if len(os.listdir(path)) == 0:
            os.rmdir(path)
    except FileNotFoundError:
        pass
    return False
