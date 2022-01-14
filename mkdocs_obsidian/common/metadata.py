"""
Update metadata in the file, if option is used.
"""

import os
import re
from pathlib import Path
import urllib.parse as url

import frontmatter
from mkdocs_obsidian.common import global_value as config

BASEDIR = Path(config.BASEDIR)
WEB = config.WEB
SHARE = config.SHARE


def update_frontmatter(file, link=1):
    """
    If link = 0, update the frontmatter with new publish URL
    Also, update the share state if convert_one.
    :param file: str
    :param link: int
    :return: None
    """
    metadata = open(file, "r", encoding="utf8")
    meta = frontmatter.load(metadata)
    metadata.close()
    folder = "notes"
    if meta.get("tag"):
        tag = meta["tag"]
    elif meta.get("tags"):
        tag = meta["tags"]
    else:
        tag = ""
    meta.metadata.pop("tag", None)
    meta.metadata.pop("tags", None)
    if meta.metadata.get("category"):
        folder = meta.metadata["category"]
    else:
        folder = "notes"

    with open(file, "w", encoding="utf-8") as f:
        filename = os.path.basename(file)
        filename = filename.replace(".md", "")
        if filename == os.path.basename(folder):
            filename = ""
        path_url = url.quote(f"{folder}/{filename}")
        clip = f"{WEB}{path_url}"
        meta["link"] = clip
        update = frontmatter.dumps(meta, sort_keys=False)
        meta = frontmatter.loads(update)
        if link != 1:
            meta.metadata.pop("link", None)
        elif link == 1 and SHARE == 1 and (not meta.get(SHARE)):
            meta[SHARE] = "true"
        if tag != "":
            meta["tag"] = tag
        update = frontmatter.dumps(meta, sort_keys=False)
        if re.search(r"\\U\w+", update):
            emojiz = re.search(r"\\U\w+", update)
            emojiz = emojiz.group().strip()
            raw = r"{}".format(emojiz)
            try:
                convert_emojiz = (
                    raw.encode("ascii")
                    .decode("unicode_escape")
                    .encode("utf-16", "surrogatepass")
                    .decode("utf-16")
                )
                update = re.sub(r'"\\U\w+"', convert_emojiz, update)
            except UnicodeEncodeError:
                pass
        f.write(update)
