"""
A terrifing code to convert admonition code blocks to material code blocks.
"""

import os
import re
import sys
from itertools import zip_longest
from pathlib import Path
import yaml
from mkdocs_obsidian.common import global_value as config

BASEDIR = config.BASEDIR


def code_blocks(start_list, end_list):
    """
    Check all code blocks in the contents
    :param start_list: list[int]
    :param end_list: list[int]
    :return: list[tupe[int, int]]
    """
    start_bug = []
    end_bug = []
    bug = list(zip_longest(start_list, end_list, fillvalue=-1))
    for i in bug:
        if i[0] > i[1]:
            start_bug.append(i[0])
        elif i[0] == -1:
            end_bug.append(i[1])
    merged = []
    for i in start_bug:
        for j in end_bug:
            if i < j:
                merged.append((i, j))
    no_bug = [
        (x, y)
        for x, y in zip_longest(start_list, end_list, fillvalue=-1)
        if x != -1 and x < y
    ]
    merged = no_bug + merged
    return merged


def admonition_trad(file_data):
    """
    Change all admonition to material admonition
    :param file_data: list[str]
    :return: list[str]
    """
    code_index = 0
    code_dict = {}
    start_list = []
    end_list = []
    adm_list = [
        "note",
        "seealso",
        "abstract",
        "summary",
        "tldr",
        "info",
        "todo",
        "tip",
        "hint",
        "important",
        "success",
        "check",
        "done",
        "question",
        "help",
        "faq",
        "warning",
        "caution",
        "attention",
        "failure",
        "fail",
        "missing",
        "danger",
        "error",
        "bug",
        "example",
        "exemple",
        "abstract",
        "quote",
        "cite",
    ]
    custom = []
    admonition_custom = False
    if os.path.exists(Path(f"{BASEDIR}/assets/script/custom_admonition.yml")):
        admonition_custom = Path(f"{BASEDIR}/assets/script/custom_admonition.yml")
    elif os.path.exists(Path(f"{BASEDIR}/custom_admonition.yml")):
        admonition_custom = Path(f"{BASEDIR}/custom_admonition.yml")

    if admonition_custom:
        with open(admonition_custom, "r", encoding="utf-8") as stream:
            try:
                custom = yaml.safe_load(stream)
            except yaml.YAMLError:
                sys.exit(
                    f"Error in {admonition_custom} : Your YAML frontmatter doesn't seem valid! Use https://jsonformatter.org/yaml-validator to correct it!"
                )
    adm_list = adm_list + custom
    for i in range(0, len(file_data)):
        if re.search("[`?!]{3}( ?)\w+(.*)", file_data[i]):
            start = i
            start_list.append(start)
        if re.match("^```$", file_data[i]) or re.match("--- admonition", file_data[i]):
            end = i
            end_list.append(end)
    merged = code_blocks(start_list, end_list)
    for i, j in merged:
        code = {code_index: (i, j)}
        code_index = code_index + 1
        code_dict.update(code)
    for ln in code_dict.values():
        ad_start = ln[0]
        ad_end = ln[1]
        ad_type = re.search("[`!?]{3}\+?( ?)ad-\w+", file_data[ad_start])
        if ad_type:
            ad_type = re.sub("[`!?]{3}\+?( ?)ad-", "", ad_type.group())
            adm = "b"
            if re.search("[!?]{3} ad-(\w+) (.*)", file_data[ad_start]):
                title = re.search("[!?]{3}\+? ad-(\w+) (.*)", file_data[ad_start])
                adm = "MT"
                title = title.group(2)
            first_block = re.search("ad-(\w+)", file_data[ad_start])
            if first_block:
                file_data[ad_end] = "\n"
            adm_ad_type_code = first_block.group().replace("ad-", "")
            if adm_ad_type_code not in adm_list:
                first_block = "note"
            else:
                first_block = first_block.group()
            if adm == "b":
                first_block = (
                    "\n!!! " + first_block.replace("ad-", "") + " place_title_here"
                )
            else:
                first_block = re.search(
                    "[!?]{3}\+? ad-(\w+) (.*)", file_data[ad_start]
                ).group()
                first_block = first_block.replace("ad-", "")
                title_block = '"' + title + '"'
                first_block = first_block.replace(title, title_block)

            file_data[ad_start] = re.sub(
                "[`!?]{3}( ?)ad-(.*)", first_block, file_data[ad_start]
            )
            for i in range(ad_start, ad_end):
                if adm == "b" and file_data[i] == "collapse: open":
                    file_data[ad_start] = file_data[ad_start].replace("!!!", "???")
                    file_data[i] = ""
                elif adm == "b" and "collapse:" in file_data[i]:
                    file_data[ad_start] = file_data[ad_start].replace("!!!", "???+")
                    file_data[i] = ""
                elif adm == "b" and "title:" in file_data[i]:
                    title = '"' + file_data[i].replace("title:", "").strip() + '"'
                    if title == "":
                        title = '""'
                    file_data[ad_start] = file_data[ad_start].replace(
                        "place_title_here", title
                    )
                    file_data[i] = ""

                elif "icon:" in file_data[i]:
                    file_data[i] = ""
                elif "color:" in file_data[i]:
                    file_data[i] = ""
                elif len(file_data[i]) == 1 and adm == "b":
                    file_data[i] = "\t$~$\n"
                else:
                    file_data[i] = "\t" + file_data[i]
            if "place_title_here" in file_data[ad_start]:
                file_data[ad_start] = file_data[ad_start].replace(
                    "place_title_here", ""
                )
            file_data[ad_start] = file_data[ad_start].lstrip()
            file_data[ad_end] = file_data[ad_end].lstrip()
    return file_data
