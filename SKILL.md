---
name: smart-recipe-wiki
description: 个人与家庭专属智能食谱知识库与配餐引擎。以单道菜为原子单元，核心能力：根据冰箱现有食材智能推荐搭配 X 菜 X 汤、自动生成极简补料清单、支持食材跨方言与同族平替匹配、以及提供三层渐进式受控检索。
---

# 个人与家庭智能食谱知识库 (Smart Recipe Wiki)

本 Skill 将整个食谱知识库封装为面向日常家庭做饭场景的智能配餐与检索系统。

## 核心业务场景与触发机制

当用户提及以下意图时自动触发：
1. **冰箱反查与做饭推荐**（如“家里还剩鸡蛋、丝瓜、五花肉，今晚吃什么”、“做个2菜1汤”、“我该补买什么菜”）；
2. **菜品步骤与避坑查阅**（如“水煮肉片怎么做”、“红烧茄子怎么不吸油”，支持按需附带原作者视频链接）；
3. **食材挑鲜与粗加工技巧**（如“花蛤怎么挑、怎么快速吐沙”、“瘦肉怎么切不柴”）；
4. **新增菜品消化录入**（对 `raw/` 目录的视频字幕或笔记执行 `/ingest`）；
5. **知识库质量与状态巡检**（检查未消化原料进度或全库死链）。

---

## 常用操作与脚本调用

所有内置脚本均使用 Python 原生标准库编写（无需安装任何第三方第三方库），支持跨平台运行。

### 1. 冰箱食材反查与配餐 (`/match`)
输入手头食材与目标菜品数量，动态推荐最优荤素组合，并区分“核心必买主料”与“可选提味辅料”：
```bash
python scripts/recipe_matcher.py --ingredients "鸡蛋,丝瓜,五花肉" --count 3
```

### 2. 三层受控检索 (`/search`)
* **Layer 1 (全景大纲)**：
  ```bash
  python scripts/wiki_search.py --overview
  ```
* **Layer 2 (按食材或菜名检索高密度摘要)**：
  ```bash
  python scripts/wiki_search.py --search "牛肉"
  ```
* **Layer 3 (深入加载指定菜品详情与步骤)**：
  ```bash
  python scripts/wiki_search.py --load "wiki/dishes/水煮肉片.md"
  ```

### 3. 原料消化状态检查 (`check_ingest_status`)
自动比对已生成的菜品卡片出处与 `raw/` 原始素材，精准查看已消化/待消化进度与推荐队列：
```bash
python scripts/check_ingest_status.py
```

### 4. 知识库质量巡检 (`/lint`)
巡检死链、孤儿菜品及 YAML Frontmatter 规范性：
```bash
python scripts/wiki_lint.py
```

---

## 知识库架构契约

* **`wiki/dishes/<菜名>.md`**：客观单菜原子卡片，严禁多菜捆绑。必须包含分层食材 Frontmatter（`main`, `sub`, `seasoning`）、烹饪备料耗时、原视频直达链接与决策 Abstract。
* **`wiki/ingredients/<食材>.md`**：食材挑鲜与预处理指南，记录外观鉴别、防坑红线（变质/注水/龙葵碱等）、去腥避苦与粗加工刀工，与菜谱卡片双向互通。
* **`references/ingredient_synonyms.json`**：食材同义词（如西葫芦/小瓜）与同族平替库（如龙骨/排骨/大骨），引擎自适应泛化。
* **`thoughts/notes/`**：用户个人口味心得流（不随公开仓库同步，保障个人隐私）。
