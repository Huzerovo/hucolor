#!/usr/bin/env python3
"""从 colors-definition.json 配置与 templates/ 模板生成 README.md。"""

import os
import json
import argparse

TEMPLATES = ["README.md.template"]


def loadConfig(conf):
    """从文件加载配置。"""
    with open(conf, encoding="utf-8") as fd:
        return json.load(fd)


def getPlaceHold(keys):
    """构造占位标签，如 ['dark', 'background'] -> <!-- DARK_BACKGROUND -->。"""
    if isinstance(keys, str):
        keys = [keys]
    return "<!-- " + "_".join(k.upper() for k in keys) + " -->"


def _renderMarkdown(section):
    """将一个主题分区（颜色定义列表）渲染为 markdown 表行。"""
    if not section:
        return ""
    keys = list(section[0].keys())
    rows = []
    for item in section:
        cells = []
        for k in keys:
            value = item.get(k, "")
            if value and (k.startswith("color") or k == "name"):
                value = f"`{value}`"
            cells.append(str(value))
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join(rows)


def _renderAccentDesc(accent_desc):
    """渲染语义角色映射行（语义名 -> 描述）。"""
    rows = []
    for name, desc in accent_desc.items():
        rows.append(f"| `{name}` | {desc} |")
    return "\n".join(rows)


def _replaceMarkdownThemes(content, themes):
    """替换各主题分区的占位标签。"""
    for theme, sections in themes.items():
        for section, items in sections.items():
            placeholder = getPlaceHold([theme, section])
            content = content.replace(placeholder, _renderMarkdown(items))
    return content


def _replaceMarkdown(content, config):
    content = content.replace(getPlaceHold("version"), config["version"])
    content = _replaceMarkdownThemes(content, config["themes"])
    content = content.replace(
        getPlaceHold("accent_desc"), _renderAccentDesc(config["accent_desc"])
    )
    return content


def replace(src, config, dst, ext):
    with open(src, encoding="utf-8") as fd:
        content = fd.read()

    if ext != ".md":
        raise ValueError(f"不支持的文件类型: {ext}")
    content = _replaceMarkdown(content, config)

    with open(dst, mode="w", encoding="utf-8") as fd:
        fd.write(content)


def generate(templates_dir, config, output_dir):
    """根据模板生成 README.md。"""
    for tpl in os.listdir(templates_dir):
        if tpl not in TEMPLATES:
            continue
        src = os.path.join(templates_dir, tpl)
        stem = tpl[: -len(".template")] if tpl.endswith(".template") else tpl
        ext = os.path.splitext(stem)[1].lower()
        replace(src, config, os.path.join(output_dir, stem), ext)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        "-c",
        help="配置文件路径",
        default=os.path.join(os.getcwd(), "colors-definition.json"),
    )
    parser.add_argument(
        "--templates",
        "-t",
        help="模板目录",
        default=os.path.join(os.getcwd(), "templates"),
    )
    parser.add_argument(
        "--output",
        "-o",
        help="输出目录",
        default=os.getcwd(),
    )
    args = parser.parse_args()

    if not os.path.isfile(args.config):
        raise FileNotFoundError(args.config)
    if not os.path.isdir(args.templates):
        raise FileNotFoundError(args.templates)
    if not os.path.isdir(args.output):
        os.mkdir(args.output)

    config = loadConfig(args.config)
    generate(args.templates, config, args.output)


if __name__ == "__main__":
    main()
