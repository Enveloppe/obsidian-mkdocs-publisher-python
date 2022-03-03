"""
Main program to convert file to material mkdocs.
"""

import os
import platform
import re
import shutil
import urllib.parse as url
from pathlib import Path

import frontmatter
import unidecode

from mkdocs_obsidian.common import (
    file_checking as check,
    metadata as mt,
    admonition as adm,
)


def get_image(configuration, image):
    """Check if the image exists in the VAULT

    Parameters
    ----------
    configuration: dict
    image : str

    Returns
    -------
    str:
        Path to image if True, False otherwise

    """
    VAULT_FILE = configuration["vault_file"]
    shortname = unidecode.unidecode(os.path.splitext(image)[0])
    assets = [x for x in VAULT_FILE if not x.endswith(".md")]
    for filepath in assets:
        file_name = unidecode.unidecode(os.path.splitext(os.path.basename(filepath))[0])
        if file_name == shortname:
            return filepath
    return False


def copy_image(configuration, final_text):
    """Copy the image in assets if exist

    Parameters
    ----------
    configuration: dict
    final_text : str
        Line readed
    """
    IMG = configuration["img"]
    list_text = final_text.split("!")
    if len(list_text) > 0:
        for i in list_text:
            link = re.search("(\[{2}|\().*\.(png|jpg|jpeg|gif)", i)
            if link:
                final_text = re.sub("(!?|\(|(%20)|\[|\]|\))", "", i)
                final_text = os.path.basename(final_text.split("|")[0])
                image_path = get_image(configuration, final_text)
                if (
                    image_path
                    and os.path.isfile(image_path)
                    and not image_path.endswith(".md")
                ):
                    shutil.copyfile(
                        image_path, Path(f"{IMG}/{os.path.basename(image_path)}")
                    )


def clipboard(configuration, filepath, folder):
    """Copy file URL to clipboard

    Parameters
    ----------
    configuration: dict
    filepath : str
        Path to the file
    folder: str
        Path to folder
    """
    filename = os.path.basename(filepath)
    filename = filename.replace(".md", "")
    folder_key = os.path.basename(folder)
    if filename == folder:
        filename = ""
    paste = url.quote(f"{folder_key}/{filename}")
    clip = f"{configuration['web']}{paste}"
    if platform.architecture()[1] == "":
        try:
            import pasteboard  # work with pyto

            pasteboard.set_string(clip)
        except ImportError:
            pass
    else:
        try:
            # trying to use Pyperclip
            import pyperclip

            pyperclip.copy(clip)
        except ImportError:
            print(
                "Please, report issue with your OS and configuration to check if it"
                " possible to use another clipboard manager"
            )


def file_write(configuration, filepath, contents, folder, preserve=0, meta_update=1):
    """Write the new converted file and update metadata if meta_update is 0

    Parameters
    ----------
    configuration: dict
    filepath : str, Path
        file to convert
    contents: list
        File contents
    folder: str, Path
        folderpath in publish
    preserve: int, default: 0
        Change shared state in frontmatter if 1
    meta_update: int, default: 1
        Update frontmatter if meta_update = 0

    Returns
    -------
    bool:
        True if file is created, False otherwise

    """
    SHARE = configuration["share"]
    file_name = os.path.basename(filepath)
    shortname = unidecode.unidecode(os.path.splitext(file_name)[0])
    foldername = unidecode.unidecode(Path(folder).name)
    meta = frontmatter.load(filepath)
    if contents == "":
        return False
    if preserve == 0 and not meta.get(SHARE):
        check.delete_file(filepath, folder, meta_update)
        return False
    if shortname == foldername:
        file_name = "index.md"
    with open(Path(f"{folder}/{file_name}"), "w", encoding="utf-8") as new_notes:
        for line in contents:
            new_notes.write(line)
    if meta_update == 0:
        if preserve == 1 and not meta.get(SHARE):
            meta[SHARE] = True
            mt.update_frontmatter(filepath, 1)
        else:
            mt.update_frontmatter(filepath, 0)
    return True


def read_custom(BASEDIR):
    """read custom css, selection of id for custom attribute (special hashtags)

    Parameters
    ----------
    BASEDIR: Path

    Returns
    -------
    id_css:
        List of the custom attribute CSS founded
    """
    id_css = []
    with open(
        Path(f"{BASEDIR}/docs/assets/css/custom_attributes.css"), "r", encoding="utf-8"
    ) as css:
        for i in css.readlines():
            if i.startswith("#"):
                id_css.append(i.replace("{\n", "").strip())
    return id_css


def convert_hashtags(configuration, final_text):
    """Convert configured hashtags with inline attribute CSS from custom.css

    Parameters
    ----------
    configuration: dict
    final_text: str
        A line of the contents to convert if contains hashtags
    Returns
    -------
    final_text: str
        converted line

    """
    css = read_custom(configuration["basedir"])
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
                    + "}\n"
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
                + " .hash}  \n"
            )

            final_text = final_text.replace(token[i], ial, 1)

    return final_text


def index_path(file_name, VAULT_FILE):
    """
    Get the path of a founded index.md

    Parameters
    ----------
    file_name: str
        File found to be an index
    VAULT_FILE: list[str]

    Returns
    -------
    index: str
        converted url path with category/index.md
    """
    file = [x for x in VAULT_FILE if os.path.basename(x) == file_name + ".md"]
    index = "index"
    if file:
        metadata = frontmatter.load(file[0])
        if metadata.get("category") and Path(metadata["category"]).name == file_name:
            category = str(Path(metadata["category"])).replace(
                "\\", "/"
            )  # Normalize path on Windows
            index = "/" + category + "/index.md"
    return index


def index_citation(final_text, configuration):
    """
    Allow the citation of index.md by citation with configured INDEX_KEY.
    Invert the alias and filename, replace filename by `category/index`

    Examples
    --------
    - `[[filename|(i) Alias]]`  -> `[[index|Alias]]`
    - `[[filename|(i)]]`  -> `[[index|filename]]`

    Parameters
    ----------
    configuration: dict
    final_text : str
        Line to check, wikilinks or MD links

    Returns
    -------
    final_text: str
        Return the line with alias and file name inverted

    """
    INDEX_KEY = configuration["index_key"]
    VAULT_FILE = configuration["vault_file"]
    if ") [" in final_text:
        cited = (
            re.search(
                rf"(\[{2}.*\|(.*)"
                + re.escape(INDEX_KEY)
                + r"(.*)\]{2}|\[.*"
                + re.escape(INDEX_KEY)
                + r".*]\(.*\))",
                final_text,
            )
            .group()
            .split(") [")
        )
    else:
        cited = (
            re.search(
                r"(\[{2}.*\|.*"
                + re.escape(INDEX_KEY)
                + r".*\]{2}|\[.*"
                + re.escape(INDEX_KEY)
                + r".*]\(.*\))",
                final_text,
            )
            .group()
            .split("]]")
        )
    for i in cited:
        if i != "" and not "www" in i:
            if re.search(rf"\|.*" + re.escape(INDEX_KEY) + rf".*", i):
                file_name = (
                    re.search(rf"\|.*" + re.escape(INDEX_KEY) + rf".*", i)
                    .group()
                    .replace(INDEX_KEY, "")
                    .replace("|", "")
                    .strip()
                )
                if len(file_name) == 0:
                    file_name = (
                        re.search("(.*)\|", i)
                        .group(1)
                        .replace("|", "")
                        .replace("[", "")
                        .replace(INDEX_KEY, "")
                    )
                index = index_path(file_name, VAULT_FILE)
                cite = f"[[{index}|" + file_name.strip()
                final_text = final_text.replace(i, cite)
            elif re.search(r"(.*)" + re.escape(INDEX_KEY) + r"(.*)\]", i):
                file_name = re.search(r"(.*)" + re.escape(INDEX_KEY) + r"(.*)\]", i)
                file_name = (
                    file_name.group()
                    .replace(INDEX_KEY, "")
                    .replace("[", "")
                    .replace("]", "")
                )
                if len(file_name) == 0:
                    file_name = re.search("\]\((.*)", i).group(1).replace(")", "")
                index = index_path(file_name, VAULT_FILE)
                cite = "[" + file_name + f"]({index})"
                final_text = (
                    final_text.replace(i, cite)
                    .replace("))", ")")
                    .replace("[[", "[")
                    .replace("]]", "]")
                )
    return final_text


def file_convert(configuration, filepath, force=0):
    """Read the filepath and convert each line based on regex condition.

    Parameters
    ----------
    configuration: dict
    filepath : str
        path to file
    force : int, default: 0
        deletion option

    Returns
    -------
    final: list[str]
        converted contents, ready for writing.

    """
    final = []

    INDEX_KEY = configuration["index_key"]
    SHARE = configuration["share"]
    meta = frontmatter.load(filepath)
    lines = meta.content.splitlines(True)
    if force != 1 and not meta.get(SHARE):
        return final
    lines = adm.admonition_trad(configuration["basedir"], lines)
    for line in lines:
        final_text = line
        if not final_text.strip().endswith("%%") and not final_text.strip().startswith(
            "%%"
        ):
            # Skip obsidian comments
            # Check and copy image
            copy_image(configuration, final_text)
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
            if re.search(
                rf"\[\[?(.*)" + re.escape(INDEX_KEY) + r"(.*)\]\]?", final_text
            ):
                # fix pagination.indexes page citation, exclude image/embed file
                final_text = index_citation(final_text, configuration)
            if re.search("#\w+", final_text) and not re.search(
                "(`|\[{2}|\()(.*)#(.*)(`|\]{2}|\))", final_text
            ):  # search hashtags not in link
                # Convert hashtags
                final_text = convert_hashtags(configuration, final_text)
            elif re.fullmatch(
                "\\\\", final_text.strip()
            ):  # New line when using "\" in obsidian filepath
                final_text = "\n"

            elif final_text == "```\n":
                # fix code newlines for material mkdocs
                final_text = final_text + "\n"

            final.append(final_text)
    for k, v in meta.metadata.items():
        if isinstance(v, str):
            meta.metadata[k] = '"' + v + '"'
    meta_list = [f"{k}: {v}\n" for k, v in meta.metadata.items()]
    meta_list.insert(0, "---\n")
    meta_list.insert(len(meta_list) + 1, "---\n")
    final = meta_list + final
    return final
