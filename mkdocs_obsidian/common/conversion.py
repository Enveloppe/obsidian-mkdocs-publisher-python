"""
Main program to convert file to material mkdocs.
"""

import os
import re
import shutil
import sys
import urllib.parse as url
from pathlib import Path

import frontmatter
import unidecode

from mkdocs_obsidian.common import (
    file_checking as check,
    global_value as config,
    metadata as mt,
    admonition as adm,
)

BASEDIR = Path(config.BASEDIR)
VAULT = Path(config.VAULT)
VAULT_FILE = config.VAULT_FILE
SHARE = config.SHARE


def get_image(image):
    """
    Check if the image exists in the VAULT
    :param image: str
    :return: bool or filepath to image
    """
    for filepath in VAULT_FILE:
        if unidecode.unidecode(os.path.basename(filepath)) in unidecode.unidecode(
            image
        ):
            return filepath
    return False


def copy_image(final_text):
    """
    Copy the image if exist
    :param final_text: str
    :return: None
    """
    list_text = final_text.split("!")
    if len(list_text) > 0:
        for i in list_text:
            link = re.search("(\[{2}|\().*\.(png|jpg|jpeg|gif)", i)
            if link:
                final_text = re.sub("(!|\(|(%20)|\[|\]|\))", "", i)
                final_text = os.path.basename(final_text.split("|")[0])
                image_path = get_image(final_text)
                if image_path and os.path.isfile(image_path):
                    shutil.copyfile(
                        image_path, Path(f"{config.IMG}/{os.path.basename(image_path)}")
                    )


def clipboard(filepath, folder):
    """
    Copy file URL to clipboard
    :param filepath: str
    :param folder: str
    :return: None
    """
    filename = os.path.basename(filepath)
    filename = filename.replace(".md", "")
    folder_key = os.path.basename(folder)
    if filename == folder:
        filename = ""
    paste = url.quote(f"{folder_key}/{filename}")
    clip = f"{config.WEB}{paste}"
    if sys.platform == "ios":
        try:
            import pasteboard  # work with pyto

            pasteboard.set_string(clip)
        except ImportError:
            try:
                import clipboard  # work with pytonista

                clipboard.set(clip)
            except ImportError:
                print(
                    "Please, report issue with your OS and configuration to check if it possible to use another clipboard manager"
                )
    else:
        try:
            # trying to use Pyperclip
            import pyperclip

            pyperclip.copy(clip)
        except ImportError:
            print(
                "Please, report issue with your OS and configuration to check if it possible to use another clipboard manager"
            )


def file_write(file, contents, folder, preserve=0, meta_update=1):
    """
        - Delete file if stoped sharing
        - Write file if SHARE = true
        - Update frontmatter if meta_update = 0
    :param file: str
    :param contents: list[str]
    :param folder: pathlib
    :param preserve: int(bool)
    :param meta_update: int(bool)
    :return: bool
    """
    file_name = os.path.basename(file)
    meta = frontmatter.load(file)
    if contents == "":
        return False
    if preserve == 0 and not meta.get(SHARE):
        check.delete_file(file, folder, meta_update)
        return False
    if os.path.splitext(file_name)[0] == os.path.basename(folder):
        file_name = "index.md"
    with open(Path(f"{folder}/{file_name}"), "w", encoding="utf-8") as new_notes:
        for line in contents:
            new_notes.write(line)
    if meta_update == 0:
        if preserve == 1 and not meta.get(SHARE):
            meta[SHARE] = True
            mt.update_frontmatter(file, 1)
        else:
            mt.update_frontmatter(file, 0)
    return True


def read_custom():
    """
    read custom css
    :return: list[str]
    """
    id_css = []
    with open(
        Path(f"{BASEDIR}/docs/assets/css/custom_attributes.css"), "r", encoding="utf-8"
    ) as css:
        for i in css.readlines():
            if i.startswith("#"):
                id_css.append(i.replace("{\n", "").strip())
    return id_css


def convert_hashtags(final_text):
    """
    Convert configured hashtags with ial CSS from custom.css
    :param final_text: str
    :return: str
    """
    css = read_custom()
    token = re.findall("#\w+", final_text)
    token = list(set(token))
    for i in range(0, len(token)):
        if token[i] in css:
            final_text = final_text.replace(token[i], "")
            if final_text.startswith("#"):
                heading = re.findall("#", final_text)
                heading = "".join(heading)
                ial = (
                    heading
                    + " **"
                    + final_text.replace("#", "").strip()
                    + "**{: "
                    + token[i]
                    + "}  \n"
                )
            else:
                ial = "**" + final_text.strip() + "**{: " + token[i] + "}  \n"
            final_text = final_text.replace(final_text, ial)
        else:
            ial = (
                "**"
                + token[i].replace("#", " ").strip()
                + "**{: "
                + token[i].strip()
                + "}{: .hash}  \n"
            )
            final_text = final_text.replace(token[i], ial, 1)
    return final_text


def file_convert(file, force=0):
    """
    Read the file and convert each line based on regex condition.
    :param file: str
    :param force: int(bool)
    :return: list[str]
    """
    final = []
    meta = frontmatter.load(file)
    lines = meta.content.splitlines(True)
    if force != 1 and not meta.get(SHARE):
        return final
    lines = adm.admonition_trad(lines)
    for line in lines:
        final_text = line
        if not final_text.strip().endswith("%%") and not final_text.strip().startswith(
            "%%"
        ):
            # Skip obsidian comments
            # Check and copy image
            copy_image(final_text)
            if not "`" in final_text:
                final_text = re.sub(
                    "\%{2}(.*)\%{2}", "", final_text
                )  # remove obsidian comments
            if (
                re.search(r"\\U\w+", final_text) and not "Users" in final_text
            ):  # Fix emoji if bug because of frontmatter
                emojiz = re.search(r"\\U\w+", final_text)
                emojiz = emojiz.group().strip().replace('"', "")
                convert_emojiz = (
                    emojiz.encode("ascii")
                    .decode("unicode-escape")
                    .encode("utf-16", "surrogatepass")
                    .decode("utf-16")
                )
                final_text = re.sub(r"\\U\w+", convert_emojiz, final_text)
            if re.search("#\w+", final_text) and not re.search(
                "(`|\[{2}|\()(.*)#(.*)(`|\]{2}|\))", final_text
            ):  # search hashtags not in link
                # Convert hashtags
                final_text = convert_hashtags(final_text)
            elif re.fullmatch(
                "\\\\", final_text.strip()
            ):  # New line when using "\" in obsidian file
                final_text = "\n"
            # Remove embed files (and link to them)
            elif re.search("!\[{2}(.*)\]{2}", final_text):
                embed = re.search("!\[{2}(.*)\]{2}", final_text)
                embed = embed.group().split("]")
                for i in embed:
                    if not re.search("(png)|(jpg)|(gif)|(jpeg)", i):
                        remove = i.replace("!", "")
                        final_text = final_text.replace(i, remove)
            elif final_text == "```\n":
                # fix code newlines for material mkdocs
                final_text = final_text + "\n"
            # remove inline block citation
            elif re.search("\^[A-Za-z0-9]+$", final_text):
                final_text = re.sub("\^[A-Za-z0-9]+$", "", final_text).strip()
            elif re.search("#\^[A-Za-z0-9]+\]{2}", final_text):
                final_text = re.sub("#\^[A-Za-z0-9]+", "", final_text).strip()

            final.append(final_text)
    for k, v in meta.metadata.items():
        if isinstance(v, str):
            meta.metadata[k] = '"' + v + '"'
    meta_list = [f"{k}: {v}\n" for k, v in meta.metadata.items()]
    meta_list.insert(0, "---\n")
    meta_list.insert(len(meta_list) + 1, "---\n")
    final = meta_list + final
    return final
