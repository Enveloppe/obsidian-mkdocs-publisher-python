"""
All function intended to check the file and their path.
"""

import glob
import os
import sys
from pathlib import Path

import frontmatter
import yaml
from unidecode import unidecode

from mkdocs_obsidian.common import metadata as mt


def config_exclude(BASEDIR):
    """
    A simple script to add compatibility with older version : the renaming of .exclude_folder to .exclude
    Parameters
    ----------
    BASEDIR : Path
        Base folder
    Returns
    -------
    config_folder: Path
        The path of exclude.yml

    """
    config_folder = Path(f"{BASEDIR}/exclude_folder.yml")
    if not os.path.exists(config_folder):
        config_folder = Path(f"{BASEDIR}/exclude.yml")
    return config_folder


def exclude(filepath, key, BASEDIR):
    """
    Check if a file is in `exclude.yml`.
    Parameters
    ----------
    BASEDIR: Path
        Base directory absolute path
    filepath: str
        Path to the file to check
    key: str

    Returns
    -------
    bool:
        True if filepath is in the list.
    """
    config_folder = config_exclude(BASEDIR)
    if os.path.exists(config_folder):
        with open(config_folder, "r", encoding="utf-8") as file_config:
            try:
                folder = yaml.safe_load(file_config)
            except yaml.YAMLError as exc:
                print(f"[red bold]Error in [u]{folder}[/] : {exc}")
                sys.exit(2)
        excluded_folder = folder.get(key, "")
        return any(str(Path(file)) in filepath for file in excluded_folder)
    return False


def delete_not_exist(configuration):
    """
    Removes files that have been deleted from the vault unless they are in `exclude.yml[files]` and always delete if founded file is in `exclude.yml[folder]`
    Parameters
    ----------
    configuration: dict
        dictionnary configuration
    Returns
    -------
    info: list[str]
        List of deleted file
    """
    BASEDIR = configuration["basedir"]
    VAULT_FILE = configuration["vault_file"]
    vault_file = []
    info = []
    excluded = []
    important_folder = ["assets", "css", "js", "logo", "script"]
    docs = Path(f"{BASEDIR}/docs/**")
    for note in VAULT_FILE:
        vault_file.append(os.path.basename(note))
        if exclude(note, "folder", BASEDIR):
            excluded.append(os.path.basename(note))
    for file in glob.iglob(str(docs), recursive=True):
        if (
            not any(i in file for i in important_folder)
            and not exclude(file, "files", BASEDIR)
            and (
                os.path.basename(file) not in vault_file
                or os.path.basename(file) in excluded
            )
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


def diff_file(filepath, folder, contents, update=0):
    """Check the difference between file in vault and file in publish.
    Check if the new converted file = the file on publish.

    Parameters
    ----------
    filepath : str
        filepath of source file
    folder: str | Path
        folder found in category of the source file
    contents: list[str]
        Contents of the file to check
    update: int, default: 0
        check if update is forced

    Returns
    -------
    bool:
        True if file are different or don't exist

    """
    filename = os.path.basename(filepath)
    shortname = unidecode(os.path.splitext(filename)[0])
    foldername = unidecode(Path(folder).name)
    if check_file(filename, folder) == "EXIST":
        if update == 1:
            return False
        if foldername == shortname:
            filename = "index.md"
        note = Path(f"{folder}/{filename}")
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


def retro(file, opt=0):
    """Remove metadata from note

    Parameters
    ----------
    file: str | Path | list
    opt: int, default: 0
        if file is a list (note's content) or a filepath
        - 0: Filepath
        - 1: note's content
    Returns
    -------
    list[str]:
        the frontmatter of the note

    """
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


def create_folder(category, configuration, share=0):
    """
    create a folder based on the category key as 'folder1/folder2/.../' and return the folder path. Return default path in case of error/none category
    Parameters
    ----------
    configuration : dict
        Configuration dictionnary.
    category : str
        Category frontmatter key
    share: int, default: 0
        status of the note
    Returns
    -------
    folder: Path
        Created folder path

    """
    BASEDIR = configuration["basedir"]
    POST = configuration["post"]

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
    """check the modification time : return true if file modified since the last push.

    Parameters
    ----------
    filepath : str
        filepath's file to check
    folder: str | Path
        folder in the blog
    update : int
        skip check if 0 (force update)

    Returns
    -------
    bool:
        True if file doesn't exist, force update or file modified since the last push.
    """
    if update == 0:
        return True  # Force update
    filename = os.path.basename(filepath)
    filepath = Path(filepath)
    note = Path(f"{folder}/{filename}")
    if os.path.isfile(note):
        return filepath.stat().st_mtime > note.stat().st_mtime
    return True  # file doesn't exist


def skip_update(filepath, folder, update):
    """check if file exist + update is false

    Parameters
    ----------
    filepath: str
        file's filepath to check existence
    folder: str | Path
        folder's path
    update: int
        Update key state

    Returns
    -------
    bool:
        Return True if file exist and update is False, False otherwise
    """
    filepath = Path(filepath)
    return update == 1 and check_file(filepath, folder) == "EXIST"


def check_file(filepath, folder: str):
    """check if the requested file exist or not in publish.

    Parameters
    ----------
    filepath : str, Path
        filepath
    folder : str
        folderpath in publish

    Returns
    -------
    str:
        "EXIST" or "NE"

    """
    file = os.path.basename(filepath)
    shortname = unidecode(os.path.splitext(file)[0])
    foldername = unidecode(Path(folder).name)
    if foldername == shortname:
        file = "index.md"
    publish = Path(f"{folder}/{file}")
    if os.path.isfile(publish):
        return "EXIST"
    return "NE"


def delete_file(filepath, folder, meta_update=1):
    """Delete the requested file

    Parameters
    ----------
    filepath : str | Path
        filepath
    folder : str|Path
        folder path
    meta_update : int (default: 1)
        update the metadata if 0

    Returns
    -------
    bool:
        True if file is successfully deleted

    """
    path = Path(folder)
    try:
        for file in os.listdir(path):
            filename = unidecode(os.path.basename(filepath))
            filecheck = unidecode(os.path.basename(file))
            if filecheck == filename:
                os.remove(Path(f"{path}/{file}"))
                if meta_update == 0:
                    mt.update_frontmatter(filepath, configuration, 0)
                return True
        if len(os.listdir(path)) == 0:
            os.rmdir(path)
    except FileNotFoundError:
        pass
    return False
