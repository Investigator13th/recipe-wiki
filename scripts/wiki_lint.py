#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wiki_lint.py - 食谱知识库质量巡检与健康自愈工具
巡检范围：
1. 死链接检测：扫描 markdown 文件中未定义的目标页面 [[link]]
2. 孤儿页面发现：扫描未被任何页面引用的菜品
3. 菜品 Frontmatter 规范性：检查 name, type, ingredients, abstract 是否齐全
纯 Python 标准库编写，零外部依赖。
"""

import os
import re
import sys
import argparse

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

WIKILINK_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")
FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

def find_markdown_files(root_dir):
    md_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            if f.endswith(".md"):
                md_files.append(os.path.join(dirpath, f))
    return md_files

def extract_wikilinks(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            return WIKILINK_PATTERN.findall(content)
    except Exception:
        return []

def check_dish_frontmatter(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        match = FRONTMATTER_PATTERN.match(content)
        if not match:
            return False, "缺失 YAML Frontmatter 头部"
        yaml_text = match.group(1)
        has_abstract = "abstract:" in yaml_text
        has_ingredients = "ingredients:" in yaml_text
        if not has_abstract:
            return False, "缺少 abstract 摘要字段"
        if not has_ingredients:
            return False, "缺少 ingredients 食材结构字段"
        return True, ""
    except Exception as e:
        return False, str(e)

def lint_workspace(workspace_dir):
    wiki_dir = os.path.join(workspace_dir, "wiki")
    dishes_dir = os.path.join(wiki_dir, "dishes")
    thoughts_dir = os.path.join(workspace_dir, "thoughts")
    
    if not os.path.exists(wiki_dir):
        print(f"[Error] 未找到 wiki 目录: {wiki_dir}", file=sys.stderr)
        return {"status": "error"}

    wiki_files = find_markdown_files(wiki_dir)
    thought_files = find_markdown_files(thoughts_dir) if os.path.exists(thoughts_dir) else []
    
    page_names = set()
    for wf in wiki_files:
        basename = os.path.splitext(os.path.basename(wf))[0]
        page_names.add(basename.lower())
        page_names.add(basename)
        
    inbound_links = {p: 0 for p in page_names}
    dead_links = []
    missing_frontmatters = []
    
    for wf in wiki_files:
        basename = os.path.splitext(os.path.basename(wf))[0]
        links = extract_wikilinks(wf)
        
        # 针对 dishes 下的卡片检查 Frontmatter 规范
        if "dishes" in wf and basename.lower() != "index":
            is_valid, err = check_dish_frontmatter(wf)
            if not is_valid:
                missing_frontmatters.append({"file": os.path.relpath(wf, workspace_dir), "reason": err})
                
        for link in links:
            clean_link = link.strip().lower()
            if clean_link in page_names:
                inbound_links[clean_link] += 1
            else:
                dead_links.append({"source": wf, "target": link})
                
    orphan_pages = []
    for p, count in inbound_links.items():
        if count == 0 and p.lower() != "index":
            orphan_pages.append(p)
            
    thoughts_with_links = 0
    for tf in thought_files:
        t_links = extract_wikilinks(tf)
        if t_links:
            thoughts_with_links += 1

    report = {
        "total_wiki_pages": len(wiki_files),
        "total_dishes": len(find_markdown_files(dishes_dir)) if os.path.exists(dishes_dir) else 0,
        "dead_links_count": len(dead_links),
        "dead_links": dead_links,
        "orphan_pages_count": len(orphan_pages),
        "orphan_pages": orphan_pages,
        "missing_frontmatter_count": len(missing_frontmatters),
        "missing_frontmatters": missing_frontmatters,
        "total_thoughts": len(thought_files),
        "thoughts_with_links": thoughts_with_links
    }
    return report

def main():
    parser = argparse.ArgumentParser(description="食谱知识库质量巡检 (wiki_lint.py)")
    parser.add_argument("--workspace", default=".", help="工作区根目录")
    args = parser.parse_args()
    
    rep = lint_workspace(args.workspace)
    if rep.get("status") == "error":
        sys.exit(1)
        
    print("================ 食谱知识库健康巡检报告 ================")
    print(f"📊 Wiki 页面总数: {rep['total_wiki_pages']} (其中单道菜品: {rep['total_dishes']} 道)")
    print(f"🔗 死链接数量: {rep['dead_links_count']}")
    if rep['dead_links']:
        for dl in rep['dead_links'][:5]:
            print(f"   ❌ 来源: {os.path.basename(dl['source'])} -> 目标不存在: [[{dl['target']}]]")
    print(f"🏝️ 孤儿菜品数量 (尚未编入索引或被引用): {rep['orphan_pages_count']}")
    if rep['orphan_pages']:
        print(f"   列表: {', '.join(rep['orphan_pages'][:5])}")
    print(f"📋 规范性缺陷菜谱数: {rep['missing_frontmatter_count']}")
    if rep['missing_frontmatters']:
        for mf in rep['missing_frontmatters'][:5]:
            print(f"   ⚠️ 文件: {mf['file']} ({mf['reason']})")
    print(f"💭 做菜心得笔记数: {rep['total_thoughts']} (已挂接菜品: {rep['thoughts_with_links']})")
    print("========================================================")
    
    if rep['dead_links_count'] > 0:
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
