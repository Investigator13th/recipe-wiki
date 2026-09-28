#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wiki_search.py - 食谱库三层渐进式受控检索工具
1. Layer 1: --overview 输出菜谱库全局大纲与已有分类
2. Layer 2: --search <query> 仅检索并返回匹配菜品的 50~100 字 Abstract（极省 Token，快速决定做哪道）
3. Layer 3: --load <paths> 精准全量加载选定菜谱正文（安全门禁：单次最多 5 篇）
纯 Python 标准库编写，零外部依赖。
"""

import os
import sys
import re
import argparse

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

def parse_frontmatter(content):
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return {}, content
    yaml_text = match.group(1)
    body = content[match.end():]
    data = {
        "name": "",
        "tags": [],
        "prep_time": "",
        "cook_time": "",
        "abstract": "",
        "ingredients": {"main": [], "sub": [], "seasoning": []}
    }
    current_section = None
    current_sub_key = None
    for line in yaml_text.splitlines():
        line_clean = line.strip()
        if not line_clean or line_clean.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if indent == 0 and ":" in line_clean:
            k, v = line_clean.split(":", 1)
            k = k.strip()
            v = v.strip().strip("'").strip('"')
            if k == "ingredients":
                current_section = "ingredients"
                current_sub_key = None
            else:
                current_section = None
                if v.startswith("[") and v.endswith("]"):
                    data[k] = [it.strip().strip("'").strip('"') for it in v[1:-1].split(",") if it.strip()]
                else:
                    data[k] = v
        elif current_section == "ingredients":
            if indent == 2 and ":" in line_clean:
                current_sub_key = line_clean.split(":", 1)[0].strip()
                if current_sub_key not in data["ingredients"]:
                    data["ingredients"][current_sub_key] = []
            elif indent >= 4 and line_clean.startswith("- ") and current_sub_key:
                val = line_clean[2:].strip().strip("'").strip('"')
                clean_val = re.sub(r"[\(（].*?[\)）]", "", val).strip()
                if clean_val:
                    data["ingredients"][current_sub_key].append(clean_val)
    return data, body

def show_overview(workspace_dir):
    index_path = os.path.join(workspace_dir, "wiki", "index.md")
    if not os.path.exists(index_path):
        print(f"[Error] 未找到索引文件: {index_path}", file=sys.stderr)
        return
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()
    print("================ 【Layer 1: 食谱库宏观总览 (Overview)】 ================")
    print(content.strip())
    print("========================================================================")

import json

def load_synonyms_rules(workspace_dir):
    json_path = os.path.join(workspace_dir, "references", "ingredient_synonyms.json")
    synonym_groups = []
    family_rules = []
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            for k, aliases in cfg.get("synonyms", {}).items():
                synonym_groups.append(set([k] + aliases))
            for fam_name, fam_data in cfg.get("families", {}).items():
                members = fam_data.get("members", [])
                if members:
                    synonym_groups.append(set(members))
                family_rules.append((fam_name, fam_data.get("excludes", [])))
        except Exception:
            pass
    return synonym_groups, family_rules

def is_ingredient_matched(token, target, synonym_groups, family_rules):
    t = token.strip().lower()
    tgt = target.strip().lower()
    if t == tgt or t in tgt or tgt in t:
        return True, 6
    for group in synonym_groups:
        if t in group and tgt in group:
            return True, 5
    for suffix, excludes in family_rules:
        if t.endswith(suffix) and tgt.endswith(suffix):
            if not any(ex in t for ex in excludes) and not any(ex in tgt for ex in excludes):
                return True, 5
    return False, 0

def search_abstracts(workspace_dir, query, top_k=5):
    wiki_dir = os.path.join(workspace_dir, "wiki")
    if not os.path.exists(wiki_dir):
        print(f"[Error] wiki 目录不存在: {wiki_dir}", file=sys.stderr)
        return
    query_tokens = [q.strip().lower() for q in re.split(r"\s+", query) if q.strip()]
    if not query_tokens:
        print("[Warning] 查询词为空。")
        return
        
    synonym_groups, family_rules = load_synonyms_rules(workspace_dir)
    candidates = []
    
    for dirpath, _, filenames in os.walk(wiki_dir):
        for f in filenames:
            if not f.endswith(".md") or f.lower() == "index.md":
                continue
            full_path = os.path.join(dirpath, f)
            rel_path = os.path.relpath(full_path, workspace_dir)
            try:
                with open(full_path, "r", encoding="utf-8") as file:
                    content = file.read()
            except Exception:
                continue
            fm, body = parse_frontmatter(content)
            name = fm.get("name", os.path.splitext(f)[0])
            aliases = fm.get("aliases", [])
            if isinstance(aliases, str):
                aliases = [aliases]
            tags = fm.get("tags", [])
            if isinstance(tags, str):
                tags = [tags]
            abstract = fm.get("abstract", "")
            ptime = fm.get("prep_time", "")
            ctime = fm.get("cook_time", "")
            time_str = f" (备料:{ptime} 烹饪:{ctime})" if (ptime or ctime) else ""
            if not abstract:
                clean_body = re.sub(r"[#*`>\[\]\n\r]", " ", body).strip()
                abstract = (clean_body[:100] + "...") if len(clean_body) > 100 else clean_body
                is_fallback = True
            else:
                is_fallback = False
            score = 0
            name_lower = str(name).lower()
            aliases_lower = [str(a).lower() for a in aliases]
            tags_lower = [str(t).lower() for t in tags]
            abstract_lower = str(abstract).lower()
            mains = fm.get("ingredients", {}).get("main", []) if isinstance(fm.get("ingredients"), dict) else []
            if isinstance(mains, str):
                mains = [mains]
            mains_lower = [str(m).lower() for m in mains]

            for token in query_tokens:
                if token in name_lower:
                    score += 5
                # 食材主料匹配打分
                for m in mains_lower:
                    matched, s = is_ingredient_matched(token, m, synonym_groups, family_rules)
                    if matched:
                        score += s
                for a in aliases_lower:
                    if token in a:
                        score += 4
                for t in tags_lower:
                    if token in t:
                        score += 3
                if token in abstract_lower:
                    score += 1
            if score > 0:
                candidates.append({
                    "name": name,
                    "rel_path": rel_path.replace("\\", "/"),
                    "tags": tags,
                    "abstract": abstract,
                    "time_str": time_str,
                    "is_fallback": is_fallback,
                    "score": score
                })
    candidates.sort(key=lambda x: x["score"], reverse=True)
    results = candidates[:top_k]
    print(f"================ 【Layer 2: 菜品摘要检索 (Query: '{query}')】 ================")
    if not results:
        print(f"❌ 未找到与 '{query}' 相关的菜品摘要。建议放宽关键词或先通过 --overview 查阅。")
    else:
        print(f"共召回 {len(candidates)} 个候选，展示 Top {len(results)}（仅返回 Abstract 快速决策）：\n")
        for idx, item in enumerate(results, 1):
            tag_str = f" [{', '.join(item['tags'])}]" if item['tags'] else ""
            fallback_warn = " ⚠️(未配置规范Abstract，截取首部)" if item['is_fallback'] else ""
            print(f"[{idx}] 菜品: {item['name']}{item['time_str']}{tag_str}")
            print(f"    路径: {item['rel_path']}")
            print(f"    摘要: {item['abstract']}{fallback_warn}")
            print()
        print("💡 下一步：评估上述摘要。若需深读做法，使用 --load '<rel_path>' 加载完整配方与步骤。")
    print("========================================================================")

def load_entities(workspace_dir, paths_str):
    paths = [p.strip() for p in paths_str.split(",") if p.strip()]
    if not paths:
        print("[Error] 请提供要加载的菜品路径或名称。", file=sys.stderr)
        return
    if len(paths) > 5:
        print(f"⚠️ [安全门禁警告] 单次最多加载 5 个菜品，已自动截取前 5 个。", file=sys.stderr)
        paths = paths[:5]
    print(f"================ 【Layer 3: 菜品配方正文加载 (共 {len(paths)} 篇)】 ================")
    for idx, p in enumerate(paths, 1):
        target_path = os.path.join(workspace_dir, p)
        if not os.path.exists(target_path):
            found = False
            for root, _, files in os.walk(os.path.join(workspace_dir, "wiki")):
                for f in files:
                    if f.lower() == f"{p.lower()}.md" or f.lower() == p.lower():
                        target_path = os.path.join(root, f)
                        found = True
                        break
                if found:
                    break
        if not os.path.exists(target_path):
            print(f"\n--- [{idx}/{len(paths)}] ❌ 菜谱不存在: {p} ---")
            continue
        with open(target_path, "r", encoding="utf-8") as f:
            content = f.read()
        rel = os.path.relpath(target_path, workspace_dir).replace("\\", "/")
        print(f"\n📄 ---------------- [{idx}/{len(paths)}] 菜谱文件: {rel} ----------------")
        print(content.strip())
        print("--------------------------------------------------------------------------------\n")
    print("================================================================================")

def main():
    parser = argparse.ArgumentParser(description="食谱库受控检索工具")
    parser.add_argument("--workspace", default=".", help="工作区根目录")
    parser.add_argument("--overview", action="store_true", help="Layer 1: 查看菜谱大纲总览")
    parser.add_argument("--search", type=str, help="Layer 2: 关键词检索菜品并仅返回 Abstract")
    parser.add_argument("--load", type=str, help="Layer 3: 精准加载指定菜品正文（限最多5个）")
    parser.add_argument("--top-k", type=int, default=5, help="返回数量限制，默认 5")
    args = parser.parse_args()
    if args.overview:
        show_overview(args.workspace)
    elif args.search:
        search_abstracts(args.workspace, args.search, args.top_k)
    elif args.load:
        load_entities(args.workspace, args.load)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
