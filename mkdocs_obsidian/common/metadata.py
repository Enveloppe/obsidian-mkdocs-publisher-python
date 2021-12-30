import os
import re
from datetime import datetime
from pathlib import Path
import urllib.parse as url

import frontmatter
from mkdocs_obsidian.common import config

BASEDIR = Path(config.BASEDIR)
web = config.web


def update_frontmatter(file, folder, share=0, link=1):
    metadata = open(file, "r", encoding="utf8")
    meta = frontmatter.load(metadata)
    metadata.close()
    share = config.share
    folder = "notes"
    if "tag" in meta.keys():
        tag = meta["tag"]
    elif "tags" in meta.keys():
        tag = meta["tags"]
    else:
        tag = ""
    meta.metadata.pop("tag", None)
    meta.metadata.pop("tags", None)
    if "category" in meta.metadata:
        if meta.metadata["category"] != "":
            folder = meta.metadata["category"]
        else:
            folder = "notes"

    with open(file, "w", encoding="utf-8") as f:
        filename = os.path.basename(file)
        filename = filename.replace(".md", "")
        if filename == os.path.basename(folder):
            filename = ''
        path_url=url.quote(f"{folder}/{filename}")
        clip = f"{web}{folder}/{filename}"
        clip = url.quote(clip)
        meta["link"] = clip
        update = frontmatter.dumps(meta, sort_keys=False)
        meta = frontmatter.loads(update)
        if link != 1:
            meta.metadata.pop("link", None)
        elif (
            link == 1
            and share == 1
            and (share not in meta.keys() or meta[share] == "false")
        ):
            meta[share] = "true"
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
    return
