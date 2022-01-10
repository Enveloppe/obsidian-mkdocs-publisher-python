import glob
import os
import re
from pathlib import Path
import yaml
import frontmatter
from unidecode import unidecode
import datetime
from mkdocs_obsidian.common import convert_all as exclude
from mkdocs_obsidian.common import config as settings
from mkdocs_obsidian.common import metadata as mt

BASEDIR = settings.BASEDIR
post = settings.post
vault = settings.vault


def delete_not_exist():
    vault_file = []
    info = []
    excluded = []
    important_folder = ["assets", "css", "js", "logo", "script"]
    docs = Path(f"{BASEDIR}/docs/**")
    for i, j, k in os.walk(vault):
        for ki in k:
            vault_file.append(os.path.basename(ki))
            if exclude.exclude_folder(i + os.sep + ki):
                excluded.append(os.path.basename(ki))
    for file in glob.iglob(str(docs), recursive=True):
        if not (any(i in file for i in important_folder)):
            if not re.search("(README|index|CNAME)", os.path.basename(file)) and (
                os.path.basename(file) not in vault_file
                or os.path.basename(file) in excluded
            ):  # or if file in file_excluded
                try:
                    if os.path.isfile(Path(file)):
                        os.remove(Path(file))
                        folder = os.path.dirname(Path(file))
                        if len(os.listdir(folder)) == 0:
                            #Delete folder
                            os.rmdir(folder)
                        info.append(os.path.basename(file))
                except PermissionError:
                    pass
                except IsADirectoryError:
                    pass
    return info


def diff_file(file, folder, contents, update=0):
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
        except yaml.parser.ParserError:
            print("ERROR : ", file)
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
    notes = []
    if opt == 0:
        metadata = frontmatter.load(filepath)
    else:
        metadata = frontmatter.loads("".join(filepath))
    file = metadata.content.split("\n")
    for n in file:
        notes.append(n)
    return notes

def create_folder(category, share=0):
    # category form = 'folder/folder/folder'
    if category != "":
        folder = Path(f"{BASEDIR}/docs/{category}")
        try:
            if share == 0:
                folder.mkdir(parents=True, exist_ok=True)
        except OSError:
            folder = Path(post)
    else:
        folder = Path(post)
    return folder

def modification_time(filepath, folder, update):
    if update == 0:
        return True
    filename = os.path.basename(filepath)
    filepath=Path(filepath)
    note = Path(f"{folder}/{filename}")
    old_time=datetime.datetime.fromtimestamp(note.stat().st_mtime)
    new_time = datetime.datetime.fromtimestamp(filepath.stat().st_mtime)
    if new_time > old_time:
        return True
    return False

def skip_update(filepath, folder, update):
    filepath=Path(filepath)
    if update == 1 and check_file(filepath, folder) == "EXIST":
        return True
    else:
        return False


def check_file(filepath, folder):
    file = os.path.basename(filepath)
    folder_check = os.path.basename(folder)
    if file.replace(".md", "") == folder_check:
        file = "index.md"
    result = [
        os.path.basename(y)
        for x in os.walk(Path(folder))
        for y in glob.glob(os.path.join(x[0], "*.md"))
    ]
    if file in result:
        return "EXIST"
    else:
        return "NE"


def delete_file(filepath, folder, meta_update=1):
    path = Path(folder)
    try:
        for file in os.listdir(path):
            filename = unidecode(os.path.basename(filepath))
            filecheck = unidecode(os.path.basename(file))
            if filecheck == filename:
                os.remove(Path(f"{path}/{file}"))
                if meta_update == 0:
                    mt.update_frontmatter(filepath, folder, 0, 0)
                return True
        if len(os.listdir(path)) == 0:
            os.rmdir(path)
    except FileNotFoundError:
        pass
    return False
