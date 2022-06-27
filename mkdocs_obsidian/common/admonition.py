"""A terrifing code to convert admonition code blocks to material code
blocks."""

import re


def parse_title(line: str, nb: int) -> str:
    """Parse the type and title of an Obsidian's callout."""
    title = re.search('^( ?>*)*\[!(.*)\]', line)
    rest_line = re.sub('^( ?>*)*\[!(.*)\][\+\-]?', '', line)
    title = title.group(2).lower()
    if ']-' in line:
        title = '??? ' + title
    elif ']+' in line:
        title = '???+ ' + title
    else:
        title = '!!! ' + title
    if len(rest_line) > 1:
        title = title + ' "' + rest_line.strip() + '"'
    if nb > 1:
        title = '\t' * (nb-1) + title
    return title + '\n'


def callout_conversion(line: str, callout_state: bool) -> tuple[str, bool | str]:
    final_text = line
    if callout_state:
        if line.startswith('>'):
            c = re.findall('^>+', line)
            spaces = '\t' * len(c[0])
            final_text = re.sub('^>+ ?', spaces, line)
        else:
            callout_state = final_text
    return final_text, callout_state
