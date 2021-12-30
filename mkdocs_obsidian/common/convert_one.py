import os
from datetime import datetime
from pathlib import Path

import frontmatter

from mkdocs_obsidian.common import (
    file_checking as check,
    conversion as convert,
    config as gl,
)


def convert_one(ori, git, meta):
    file_name = os.path.basename(ori).upper()
    yaml_front = frontmatter.load(ori)
    priv = Path(gl.post)
    clipKey = "notes"
    if "category" in yaml_front.keys():
        priv = check.create_folder(yaml_front["category"])
        clipKey = yaml_front["category"]
    contents = convert.file_convert(ori, priv, 1)
    checkFile = convert.file_write(ori, contents, priv, 1, meta)
    if checkFile and not git:
        COMMIT = f"Pushed {file_name.lower()} to blog"
        gl.git_push(COMMIT)
        convert.clipboard(ori, clipKey)
    elif checkFile and git:
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] 🎉 Successfully converted {file_name.lower()}"
        )
