#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
recipe_matcher.py - 冰箱剩余食材智能配餐与缺料计算引擎
核心场景：根据用户现有的冰箱食材和指定菜品数量，动态组合出最优的餐食搭配（荤素搭配+干湿搭配），并输出极简补料清单。
纯 Python 标准库编写，零外部依赖。
"""

import os
import sys
import re
import argparse

# 保证 Windows PowerShell 下的 utf-8 正常输出
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

def parse_dish_file(file_path):
    """解析单道菜 MD 文件的 Frontmatter"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return None

    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return None

    yaml_text = match.group(1)
    
    # 极简 yaml 解析器，支持分层与列表
    data = {
        "name": "",
        "type": "家常热炒",
        "tags": [],
        "prep_time": "10分钟",
        "cook_time": "15分钟",
        "abstract": "",
        "source_combo": "",
        "ingredients": {"main": [], "sub": [], "seasoning": []}
    }
    
    current_section = None
    current_sub_key = None
    
    for line in yaml_text.splitlines():
        line_clean = line.strip()
        if not line_clean or line_clean.startswith("#"):
            continue
            
        indent = len(line) - len(line.lstrip())
        
        # 顶层字段
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
                    items = [it.strip().strip("'").strip('"') for it in v[1:-1].split(",") if it.strip()]
                    data[k] = items
                else:
                    data[k] = v
        elif current_section == "ingredients":
            if indent == 2 and ":" in line_clean:
                sub_k = line_clean.split(":", 1)[0].strip()
                current_sub_key = sub_k
                if current_sub_key not in data["ingredients"]:
                    data["ingredients"][current_sub_key] = []
            elif indent >= 4 and line_clean.startswith("- ") and current_sub_key:
                val = line_clean[2:].strip().strip("'").strip('"')
                # 去除括号备注，如 "丝瓜 (1根)" -> "丝瓜"
                clean_val = re.sub(r"[\(（].*?[\)）]", "", val).strip()
                if clean_val:
                    data["ingredients"][current_sub_key].append(clean_val)
                    
    if not data["name"]:
        data["name"] = os.path.splitext(os.path.basename(file_path))[0]
    data["file_path"] = file_path
    return data

def load_all_dishes(workspace_dir):
    """加载 wiki/dishes 下所有菜品卡片"""
    dishes_dir = os.path.join(workspace_dir, "wiki", "dishes")
    if not os.path.exists(dishes_dir):
        return []
    
    dishes = []
    for root, _, files in os.walk(dishes_dir):
        for f in files:
            if f.endswith(".md"):
                path = os.path.join(root, f)
                dish_data = parse_dish_file(path)
                if dish_data:
                    dishes.append(dish_data)
    return dishes

import json

def load_synonyms_config(workspace_dir):
    """从 references/ingredient_synonyms.json 动态加载同义词与同族平替库"""
    json_path = os.path.join(workspace_dir, "references", "ingredient_synonyms.json")
    synonym_groups = []
    family_rules = []
    
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            # 解析 synonyms
            for k, aliases in cfg.get("synonyms", {}).items():
                group = set([k] + aliases)
                synonym_groups.append(group)
            # 解析 families
            for fam_name, fam_data in cfg.get("families", {}).items():
                members = fam_data.get("members", [])
                excludes = fam_data.get("excludes", [])
                if members:
                    # 将显式定义的同族成员加入同族大集合
                    synonym_groups.append(set(members))
                family_rules.append((fam_name, excludes))
            return synonym_groups, family_rules
        except Exception:
            pass
            
    # 回退默认值
    synonym_groups = [
        {"番茄", "西红柿"},
        {"土豆", "马铃薯", "洋芋"},
        {"洋葱", "圆葱"},
        {"花蛤", "花甲", "蛤蜊", "文蛤"},
        {"包菜", "卷心菜", "圆白菜", "甘蓝"},
        {"青瓜", "黄瓜"},
    ]
    family_rules = [
        ("笋", ["芦笋"]),
        ("豆腐", ["千张", "腐竹", "豆皮", "豆干"]),
        ("虾", ["虾皮", "虾米", "虾干", "虾酱"]),
    ]
    return synonym_groups, family_rules

def check_ingredient_compatible(user_ing, recipe_ing, synonym_groups, family_rules):
    """
    判断用户手头的食材 user_ing 是否能匹配或替代菜谱要求的 recipe_ing
    返回: (是否匹配, 匹配说明)
    """
    u = user_ing.strip().lower()
    r = recipe_ing.strip().lower()
    
    # 1. 直接全等或直接子串包含
    if u == r:
        return True, u
    if u in r or r in u:
        return True, u
        
    # 2. 同义词匹配
    for group in synonym_groups:
        if u in group and r in group:
            return True, f"{u} (同义替代: {r})"
            
    # 3. 同族通配词尾匹配（如 冬笋 替代 鲜笋）
    for suffix, excludes in family_rules:
        if u.endswith(suffix) and r.endswith(suffix):
            if not any(ex in u for ex in excludes) and not any(ex in r for ex in excludes):
                return True, f"{u} (同类替代: {r})"
                
    return False, ""

def match_dishes(all_dishes, user_ingredients, workspace_dir="."):
    """计算每道菜与用户现有食材的匹配度（支持同义词与同族泛化替代）"""
    synonym_groups, family_rules = load_synonyms_config(workspace_dir)
    clean_user_ings = [i.strip() for i in user_ingredients if i.strip()]
    scored_dishes = []
    
    for dish in all_dishes:
        mains = dish["ingredients"].get("main", [])
        subs = dish["ingredients"].get("sub", [])
        
        matched_mains_desc = []
        matched_recipe_mains = set()
        
        for u in clean_user_ings:
            for m in mains:
                if m in matched_recipe_mains:
                    continue
                ok, desc = check_ingredient_compatible(u, m, synonym_groups, family_rules)
                if ok:
                    matched_mains_desc.append(desc)
                    matched_recipe_mains.add(m)
                    
        missing_mains = [m for m in mains if m not in matched_recipe_mains]
        
        matched_subs_desc = []
        matched_recipe_subs = set()
        
        for u in clean_user_ings:
            for s in subs:
                if s in matched_recipe_subs:
                    continue
                ok, desc = check_ingredient_compatible(u, s, synonym_groups, family_rules)
                if ok:
                    matched_subs_desc.append(desc)
                    matched_recipe_subs.add(s)
                    
        missing_subs = [s for s in subs if s not in matched_recipe_subs]
        
        # 打分逻辑：
        # 主料命中每个 +10 分；配料命中每个 +3 分；
        # 缺失主料每个 -6 分（惩罚因买菜负担大）；
        score = len(matched_recipe_mains) * 10 + len(matched_recipe_subs) * 3 - len(missing_mains) * 6
        
        # 只要有主料匹配，或者无主料但有辅料匹配
        if matched_recipe_mains or (not mains and matched_recipe_subs):
            scored_dishes.append({
                "dish": dish,
                "score": score,
                "matched_mains": matched_mains_desc,
                "missing_mains": missing_mains,
                "matched_subs": matched_subs_desc,
                "missing_subs": missing_subs
            })
            
    scored_dishes.sort(key=lambda x: x["score"], reverse=True)
    return scored_dishes

def recommend_meal_plan(scored_dishes, count=3, need_soup=True):
    """
    根据菜品类型与得分，规划出一套结构合理的组合菜单（荤素干湿搭配）
    """
    if not scored_dishes:
        return None
        
    selected = []
    selected_names = set()
    used_types = set()
    
    # 1. 若需要汤，优先挑选得分最高的汤羹
    if need_soup:
        soup_candidates = [d for d in scored_dishes if "汤" in d["dish"].get("type", "") or "羹" in d["dish"].get("type", "")]
        if soup_candidates:
            best_soup = soup_candidates[0]
            selected.append(best_soup)
            selected_names.add(best_soup["dish"]["name"])
            used_types.add("汤羹")
            
    # 2. 依次补齐其余名额，优先兼顾荤素多样性
    remaining_slots = count - len(selected)
    
    for candidate in scored_dishes:
        if len(selected) >= count:
            break
        name = candidate["dish"]["name"]
        dtype = candidate["dish"].get("type", "热炒")
        if name in selected_names:
            continue
            
        # 避免两道完全相同的类别（在名额充足时尽量多样化）
        if dtype not in used_types or len(selected) + len([d for d in scored_dishes if d["dish"]["name"] not in selected_names]) <= count:
            selected.append(candidate)
            selected_names.add(name)
            used_types.add(dtype)
            
    # 若还有空缺，按纯分数补足
    for candidate in scored_dishes:
        if len(selected) >= count:
            break
        name = candidate["dish"]["name"]
        if name not in selected_names:
            selected.append(candidate)
            selected_names.add(name)
            
    return selected

def main():
    parser = argparse.ArgumentParser(description="根据冰箱剩余食材智能推荐配餐与补料清单")
    parser.add_argument("--workspace", default=".", help="工作区根目录")
    parser.add_argument("--ingredients", "-i", required=True, help="现有食材，用逗号隔开，如：'鸡蛋,丝瓜,排骨'")
    parser.add_argument("--count", "-c", type=int, default=3, help="期望的菜品总数（如 2 菜、3 菜、4 菜，默认 3）")
    parser.add_argument("--no-soup", action="store_true", help="指定不需要汤羹（默认会自动搭配 1 道汤）")
    parser.add_argument("--url", action="store_true", help="输出对应菜品原博主视频教程链接")
    args = parser.parse_args()
    
    user_ings = [x.strip() for x in re.split(r"[,，、\s]+", args.ingredients) if x.strip()]
    if not user_ings:
        print("❌ 请输入至少一种现有食材！", file=sys.stderr)
        sys.exit(1)
        
    all_dishes = load_all_dishes(args.workspace)
    if not all_dishes:
        print(f"⚠️ 知识库中暂未发现菜品卡片（路径：wiki/dishes/*.md）。请先执行 /ingest 录入菜谱！")
        sys.exit(0)
        
    scored = match_dishes(all_dishes, user_ings, args.workspace)
    if not scored:
        print(f"🧐 现有食材【{', '.join(user_ings)}】未在当前菜谱库中匹配到合适菜品。建议扩充菜谱或放宽关键词！")
        sys.exit(0)
        
    plan = recommend_meal_plan(scored, count=args.count, need_soup=not args.no_soup)
    
    print("\n" + "=" * 65)
    print(f"🍳 冰箱食材智能配餐方案（输入食材：{', '.join(user_ings)} | 目标：{args.count} 道菜）")
    print("=" * 65)
    
    total_missing_mains = set()
    total_missing_subs = set()
    
    for idx, item in enumerate(plan, 1):
        dish = item["dish"]
        name = dish["name"]
        dtype = dish.get("type", "家常菜")
        ptime = dish.get("prep_time", "10分钟")
        ctime = dish.get("cook_time", "15分钟")
        m_used = item["matched_mains"] + item["matched_subs"]
        
        print(f"\n[{idx}] 【{name}】（类别：{dtype} | 预估耗时：备料{ptime} + 烹饪{ctime}）")
        print(f"    📖 核心摘要：{dish.get('abstract', '暂无摘要')}")
        print(f"    ✅ 消耗现有食材：{', '.join(m_used) if m_used else '使用厨房常备料'}")
        
        if item["missing_mains"]:
            print(f"    ⚠️ 缺失主料：{', '.join(item['missing_mains'])}")
            total_missing_mains.update(item["missing_mains"])
        if item["missing_subs"]:
            print(f"    ℹ️ 建议补配料：{', '.join(item['missing_subs'])}")
            total_missing_subs.update(item["missing_subs"])
            
        if args.url and dish.get("source_url"):
            print(f"    📺 视频教程：{dish.get('source_url')}")
            
    print("\n" + "-" * 65)
    print("🛒 【极简补料买菜清单】")
    if total_missing_mains:
        print(f"  🔴 必须补齐的核心主料：{', '.join(total_missing_mains)}")
    else:
        print("  🎉 核心主料已全部齐备！无需购买大件食材！")
        
    if total_missing_subs:
        print(f"  🟡 可选增色提味的配料：{', '.join(total_missing_subs)}")
    else:
        print("  🟢 配料无需补充。")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    main()
