"""
Update metadata in the file, if option is used.
"""

import os
import re
import urllib.parse as url

import frontmatter


def update_frontmatter(filepath, configuration, link=1):
    """If link = 1, update the frontmatter with new publish URL
    Also, update the share state if convert_one.

    Parameters
    ----------
    configuration: dict
    filepath: str | Path
        path to source file
    link: int, default: 1
        if 1 add link to the metadata

    """
    SHARE = configuration["share"]
    with open(filepath, "r", encoding="utf8") as metadata:
        meta = frontmatter.load(metadata)
    if meta.get("tag"):
        tag = meta["tag"]
    elif meta.get("tags"):
        tag = meta["tags"]
    else:
        tag = ""
    meta.metadata.pop("tag", None)
    meta.metadata.pop("tags", None)
    folder = meta.metadata.get("category", configuration["default_note"])

    with open(filepath, "w", encoding="utf-8") as f:
        filename = os.path.basename(filepath)
        filename = filename.replace(".md", "")
        if filename == os.path.basename(folder):
            filename = ""
        path_url = url.quote(f"{folder}/{filename}")
        clip = f"{configuration['web']}{path_url}"
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
