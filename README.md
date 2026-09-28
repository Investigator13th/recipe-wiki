# 个人与家庭智能食谱知识库 (Recipe Wiki)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Dishes: 77](https://img.shields.io/badge/Dishes-77%20Active-brightgreen.svg)](wiki/index.md)

这是一个为家庭日常做饭整理的食谱知识库与配餐工具。

主要解决做饭前的一个常见问题：**打开冰箱只剩这几样东西，不知道能做什么，也不清楚具体还差哪几样必须买的菜。**

---

## 为什么这样设计

平时看博主做饭视频，一期通常是一整套“四菜一汤”。跟着做的时候经常遇到两个问题：要么家里刚好缺其中一两道菜的主料，整套菜单就废了；要么菜谱软件给的买菜清单里混着生抽、老抽、大蒜这些厨房常备调料，看得很累。

这个仓库做了几处调整：

1. **每道菜拆成独立卡片**：存放在 `wiki/dishes/`，不再把多道菜捆成大文件。食材分为核心主料、配料辅料和常备调料。
2. **反向计算买菜清单**：输入现有的食材，脚本会推荐几道能消化的菜，并且只提示缺少的生鲜主料，不提醒油盐酱醋。
3. **食材平替与方言**：不同地区对蔬菜和肉类称呼不同（比如小瓜和西葫芦、花甲和花蛤），或者想用排骨代替龙骨。这些映射写在 `references/ingredient_synonyms.json` 里，匹配引擎会自动泛化，不需要去修改菜谱原文。
4. **无额外依赖**：检索、配餐和检查脚本都基于 Python 标准库，直接运行即可。

---

## 怎么使用

### 1. 作为 Skill 装载进 AI 智能体（WorkBuddy / Antigravity）

仓库根目录包含 `SKILL.md`，符合工作区技能规范。

* 把本仓库放在智能体的技能目录（如 `skills/recipe-wiki/`）或直接克隆为工作区。
* 在对话里直接提问：
  * *“冰箱里有鸡蛋、丝瓜和五花肉，推荐两个菜一个汤，并告诉我缺什么要买。”*
  * *“水煮肉片怎么做，有什么避坑要点？”*

### 2. 本地命令行运行

也可以直接在终端跑脚本：

* **按现有食材配餐**：
  ```bash
  python scripts/recipe_matcher.py --ingredients "鸡蛋,丝瓜,五花肉" --count 3
  ```
* **分层检索菜谱**：
  ```bash
  # 查看大纲
  python scripts/wiki_search.py --overview
  # 搜特定食材或菜名摘要
  python scripts/wiki_search.py --search "牛肉"
  # 查看详细做法
  python scripts/wiki_search.py --load "wiki/dishes/水煮肉片.md"
  ```
* **检查知识库格式与死链**：
  ```bash
  python scripts/wiki_lint.py
  ```
* **查看原料消化进度**：
  ```bash
  python scripts/check_ingest_status.py
  ```

---

## 当前状态与进度

* **2026-09-28 更新**：目前已从原始视频素材中编译整理出 **77 道** 单菜卡片，分类覆盖荤菜、小炒、青菜、汤和凉菜。
* **待整理原料**：`raw/` 目录下存放了视频原字幕与素材，目前还有 450 篇待消化（阿蔡 122 篇，村驴 328 篇），后续会陆续抽空整理成卡片。

---

## 目录结构

```text
recipe/
├── SKILL.md                          # 智能体 Skill 配置
├── AGENTS.md                         # 知识库维护契约
├── README.md                         # 说明文件
├── references/
│   └── ingredient_synonyms.json     # 食材同义词与平替字典
├── raw/                              # 原始字幕语料（只读）
│   ├── 阿蔡/
│   └── 村驴/
├── wiki/                             # 结构化菜谱
│   ├── index.md                      # 菜品分类索引
│   └── dishes/                       # 单道菜卡片（77 篇）
└── scripts/                          # 辅助脚本
    ├── recipe_matcher.py             # 冰箱配餐引擎
    ├── wiki_search.py                # 菜谱受控检索
    ├── wiki_lint.py                  # 格式与死链巡检
    └── check_ingest_status.py        # 原料消化追踪
```

---

## 致谢

菜谱步骤与实操经验整理自两位博主公开分享的做饭视频：

* **[@村驴](https://space.bilibili.com/417298480)**
* **[@蔡盛坤 (阿蔡美食雕刻)](https://space.bilibili.com/472102908)**

*注：`raw/` 下的原始文字仅用于个人学习和非营利性整理，版权归原作者所有。*

如果你有其他讲解细致、适合家常复刻的美食博主推荐，欢迎在 Issues 里留个主页或视频链接。

---

## 开源协议

本项目使用 [MIT License](LICENSE)。
