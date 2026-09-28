#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_ingest_status.py - 原材料消化状态追踪工具
功能：通过比对 wiki/dishes/*.md 中的 source_combo 字段与 raw/ 下的文件名，精确计算已消化与未消化的原料清单。
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

def extract_source_combo(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return ""
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return ""
    yaml_text = match.group(1)
    for line in yaml_text.splitlines():
        if line.strip().startswith("source_combo:"):
            val = line.split(":", 1)[1].strip().strip("'").strip('"')
            return val
    return ""

def get_ingest_status(workspace_dir, sub_dir="阿蔡"):
    dishes_dir = os.path.join(workspace_dir, "wiki", "dishes")
    raw_dir = os.path.join(workspace_dir, "raw", sub_dir)
    
    if not os.path.exists(raw_dir):
        print(f"[Error] 原始素材目录不存在: {raw_dir}", file=sys.stderr)
        return None
        
    # 1. 扫描所有已入库菜品的 source_combo
    ingested_sources = set()
    dish_count_by_source = {}
    
    if os.path.exists(dishes_dir):
        for f in os.listdir(dishes_dir):
            if f.endswith(".md"):
                path = os.path.join(dishes_dir, f)
                src = extract_source_combo(path)
                if src:
                    ingested_sources.add(src)
                    dish_count_by_source[src] = dish_count_by_source.get(src, 0) + 1
                    
    # 2. 扫描 raw 下的所有材料
    raw_files = [f for f in os.listdir(raw_dir) if f.endswith(".md")]
    
    ingested_files = []
    pending_files = []
    
    for rf in sorted(raw_files):
        # 匹配：文件名是否包含已被引用的 source 字符串，或 source 是否包含文件名核心
        # 归一化对比
        matched = False
        rf_clean = rf.replace("【阿蔡美食雕刻】—", "").replace("【村驴】—", "")
        for src in ingested_sources:
            if src in rf or rf in src or src in rf_clean or rf_clean in src:
                matched = True
                ingested_files.append((rf, dish_count_by_source.get(src, 1)))
                break
        if not matched:
            pending_files.append(rf)
            
    return {
        "total_raw": len(raw_files),
        "ingested_count": len(ingested_files),
        "pending_count": len(pending_files),
        "ingested_files": ingested_files,
        "pending_files": pending_files
    }

def main():
    parser = argparse.ArgumentParser(description="查看 Raw 原材料的 Ingest 消化进度")
    parser.add_argument("--workspace", default=".", help="工作区根目录")
    parser.add_argument("--source", default="阿蔡", help="原料子目录名称（如 阿蔡、村驴）")
    parser.add_argument("--limit", type=int, default=10, help="展示待消化文件的数量上限")
    args = parser.parse_args()
    
    status = get_ingest_status(args.workspace, args.source)
    if not status:
        sys.exit(1)
        
    print(f"\n================ 【Raw 素材 Ingest 消化进度报告 - {args.source}】 ================")
    print(f"📦 原料总数: {status['total_raw']} 篇")
    print(f"✅ 已完成消化: {status['ingested_count']} 篇")
    print(f"⏳ 待消化入库: {status['pending_count']} 篇")
    print(f"📈 进度比例: {status['ingested_count'] / status['total_raw'] * 100:.1f}%\n")
    
    if status['ingested_files']:
        print("--- 已消化原材料明细 ---")
        for f, dcount in status['ingested_files']:
            print(f"  ✓ {f} (产出单菜: {dcount} 道)")
            
    print(f"\n--- 待消化候选推荐 (前 {min(args.limit, len(status['pending_files']))} 篇) ---")
    for idx, f in enumerate(status['pending_files'][:args.limit], 1):
        print(f"  [{idx}] {f}")
    print("================================================================================")

if __name__ == "__main__":
    main()
