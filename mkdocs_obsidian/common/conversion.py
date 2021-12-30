import os
import re
from pathlib import Path
import unidecode
import frontmatter
import sys
import shutil

from mkdocs_obsidian.common import (
    file_checking as check,
    config,
    metadata as mt,
    admonition as adm,
)

BASEDIR = Path(config.BASEDIR)
vault = Path(config.vault)


def get_image(image):
    for sub, dirs, files in os.walk(vault):
        for file in files:
            filepath = sub + os.sep + file
            if unidecode.unidecode(image) in unidecode.unidecode(file):
                return filepath
    return False


def copy_image(final_text):
    list = final_text.split("!")
    if len(list) > 0:
        for i in list:
            link = re.search("(\[{2}|\().*\.(png|jpg|jpeg|gif)", i)
            if link:
                final_text = re.sub("(!|\(|(%20)|\[|\]|\))", "", i)
                final_text = os.path.basename(final_text.split("|")[0])
                image_path = get_image(final_text)
                if image_path:
                    shutil.copyfile(image_path, f"{config.img}/{final_text}")


def clipboard(filepath, folder):
    filename = os.path.basename(filepath)
    filename = filename.replace(".md", "")
    filename = filename.replace(" ", "-")
    folder_key = os.path.basename(folder).replace("_", "")
    clip = f"{config.web}{folder_key}/{filename}"
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


def file_write(file, contents, folder, option=0, meta=0):
    file_name = os.path.basename(file)
    meta = frontmatter.load(file)
    share = config.share
    if contents == "":
        return False
    elif not share in meta or meta[share] == False:
        check.delete_file(file, folder)
        return False
    else:
        if file_name == os.path.basename(folder):
            file_name = "index"
        new_notes = open(f"{folder}/{file_name}", "w", encoding="utf-8")
        for line in contents:
            new_notes.write(line)
        new_notes.close()
        if meta == 0:
            if option == 1:
                if share not in meta.keys() or meta[share] is False:
                    meta[share] = True
                    update = frontmatter.dumps(meta)
                    meta = frontmatter.loads(update)
                    mt.update_frontmatter(file, folder, 1)
                else:
                    mt.update_frontmatter(file, folder, 0)
            else:
                mt.update_frontmatter(file, folder, 0)
        return True


def read_custom():
    css = open(
        Path(f"{BASEDIR}/docs/assets/css/custom_attributes.css"), "r", encoding="utf-8"
    )
    id = []
    css_data = css.readlines()
    for i in css_data:
        if i.startswith("#"):
            id.append(i.replace("{\n", "").strip())
    css.close()
    return id


def convert_hashtags(final_text):
    css = read_custom()
    token = re.findall("#\w+", final_text)
    token = list(set(token))
    for i in range(0, len(token)):
        if token[i] in css:
            final_text = final_text.replace(token[i], "")
            if final_text.startswith("#"):
                heading = re.findall("#", final_text)
                heading = "".join(heading)
                IAL = (
                    heading
                    + " **"
                    + final_text.replace("#", "").strip()
                    + "**{: "
                    + token[i]
                    + "}  \n"
                )
            else:
                IAL = "**" + final_text.strip() + "**{: " + token[i] + "}  \n"
            final_text = final_text.replace(final_text, IAL)
        else:
            IAL = (
                "**"
                + token[i].replace("#", " ").strip()
                + "**{: "
                + token[i].strip()
                + "}{: .hash}  \n"
            )
            final_text = final_text.replace(token[i], IAL, 1)
    return final_text


def file_convert(file, folder, option=0):
    final = []
    path_folder = str(folder).replace(f"{BASEDIR}", "")
    path_folder = path_folder.replace(os.sep, "")
    path_folder = path_folder.replace("_", "")
    meta = frontmatter.load(file)
    lines = meta.content.splitlines(True)
    share = config.share
    if option != 1:
        if share not in meta.keys() or meta[share] is False:
            return final
    lines = adm.admonition_trad(lines)
    for ln in lines:
        final_text = ln
        if not final_text.strip().endswith("%%") and not final_text.strip().startswith(
            "%%"
        ):
            copy_image(final_text)

            if not "`" in final_text:
                final_text = re.sub("\%{2}(.*)\%{2}", "", final_text)
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
            ):
                # Hashtags
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
            elif final_text == '```\n':
                final_text = final_text + '\n'
            elif re.search('\^[A-Za-z0-9]+$', final_text):
                final_text = re.sub('\^[A-Za-z0-9]+$','', final_text).strip()
            elif re.search('#\^[A-Za-z0-9]+\]{2}', final_text):
                final_text = re.sub('#\^[A-Za-z0-9]+', '', final_text).strip()

            final.append(final_text)
    meta_list = [f"{k}: {v}  \n" for k, v in meta.metadata.items()]
    meta_list.insert(0, "---  \n")
    meta_list.insert(len(meta_list) + 1, "---  \n")
    final = meta_list + final
    return final
