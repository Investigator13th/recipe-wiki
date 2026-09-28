# 🍳 个人与家庭智能食谱知识库 (Recipe Wiki)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Dishes: 77](https://img.shields.io/badge/Dishes-77%20Active-brightgreen.svg)](wiki/index.md)
[![Ingredients: 10](https://img.shields.io/badge/Ingredients-10%20Guides-orange.svg)](wiki/index.md)

这是一个为家庭日常做饭整理的食谱知识库与配餐工具。

主要解决做饭前的一个常见问题：**打开冰箱只剩这几样东西，不知道能做什么，也不清楚具体还差哪几样必须买的菜。**

---

## 💡 为什么这样设计

平时看博主做饭视频，一期通常是一整套“四菜一汤”。跟着做的时候经常遇到两个问题：要么家里刚好缺其中一两道菜的主料，整套菜单就废了；要么菜谱软件给的买菜清单里混着生抽、老抽、大蒜这些厨房常备调料，看得很累。此外，视频前半段很有价值的“菜市场怎么挑菜、怎么去腥改刀”，往往没有被结构化记录。

这个仓库做了几处调整：

1. 🥩 **每道菜拆成独立卡片**：存放在 `wiki/dishes/`，不再把多道菜捆成大文件。食材分为核心主料、配料辅料和常备调料。
2. 🥦 **食材挑鲜与预处理独立成网**：博主视频前半段在教挑菜、去腥和粗加工（比如花蛤原海水极速吐沙、瘦肉剔筋上浆）。这部分知识独立存入 `wiki/ingredients/`，与菜谱卡片双向互通，解决“买菜挑不对、粗加工踩雷”的问题。
3. 🛒 **反向计算买菜清单**：输入现有的食材，脚本会推荐几道能消化的菜，并且只提示缺少的生鲜主料，不提醒油盐酱醋。
4. 🔄 **食材平替与方言**：不同地区对蔬菜和肉类称呼不同（比如小瓜和西葫芦、花甲和花蛤），或者想用排骨代替龙骨。这些映射写在 `references/ingredient_synonyms.json` 里，匹配引擎会自动泛化，不需要去修改菜谱原文。
5. ⚡ **无额外依赖**：检索、配餐和检查脚本都基于 Python 标准库，直接运行即可。

---

## 🚀 怎么使用

### 1. 🤖 作为 Skill 装载进 AI 智能体（WorkBuddy / Antigravity）

仓库根目录包含 `SKILL.md`，符合工作区技能规范。

* 把本仓库放在智能体的技能目录（如 `skills/recipe-wiki/`）或直接克隆为工作区。
* 在对话里直接提问：
  * 🗣️ *“冰箱里有鸡蛋、丝瓜和五花肉，推荐两个菜一个汤，并告诉我缺什么要买。”*
  * 🗣️ *“水煮肉片怎么做，有什么避坑要点？”*
  * 🗣️ *“花蛤怎么挑？买回来怎么快速吐沙？”*

### 2. 💻 本地命令行运行

也可以直接在终端跑脚本：

* 🍳 **按现有食材配餐（可附带视频链接）**：
  ```bash
  python scripts/recipe_matcher.py --ingredients "鸡蛋,丝瓜,五花肉" --count 3 --url
  ```
* 🔍 **分层检索菜谱与食材指南**：
  ```bash
  # 查看大纲
  python scripts/wiki_search.py --overview
  # 搜特定食材或菜名摘要（可查看视频原出处）
  python scripts/wiki_search.py --search "牛肉"
  # 查看详细做法
  python scripts/wiki_search.py --load "wiki/dishes/水煮肉片.md"
  ```
* 🩺 **检查知识库格式与死链**：
  ```bash
  python scripts/wiki_lint.py
  ```
* 📈 **查看原料消化进度**：
  ```bash
  python scripts/check_ingest_status.py
  ```

---

## 📊 当前状态与进度

### 📅 2026-09-28 架构重大升级与内容更新

本次更新不仅大幅扩充了菜谱数量，更针对知识库架构做了关键演进，实现从“单向查做菜步骤”到“买菜挑鲜 ➔ 粗加工 ➔ 智能配餐 ➔ 视频复刻”的全链路闭环：

1. 🧱 **正交双网架构落地（菜品网 + 食材网）**：
   * **烹饪配餐网 (`wiki/dishes/`)**：已编译整理出 **77 道** 单菜原子卡片，分类覆盖硬荤大菜、半荤小炒、清口青菜、养生汤羹与凉菜卤味。
   * **挑鲜预处理网 (`wiki/ingredients/`)**：新增 **10 篇** 核心食材选购与预处理指南（花蛤、猪瘦肉、鸡腿、冬瓜、白萝卜、蒜苗、秋葵、旺螺、黄瓜、土豆），沉淀菜市场挑菜心法、防坑红线（如防发芽土豆、防死螺死蛤）、原产地海水 5 分钟吐沙与去筋上浆技巧，并通过 `[[wikilink]]` 与单道菜建立双向链接。
2. 📺 **教程直达链路打通（全量回填原视频源）**：
   * 全量 77 道菜谱均已在 Frontmatter 注入原作者 B 站视频直达链接（`source_url`）。
   * 配餐引擎与受控检索新增 `--url` 开关，在终端或 AI 对话中按需一键直达原汁原味的动态视频演示。
3. 📦 **原材料消化进度**：
   * `raw/` 目录下存放了视频原字幕与素材，目前仍有 450 篇待消化（阿蔡 122 篇，村驴 328 篇），后续将结合常见食材高频需求持续增量编译。

---

## 📂 目录结构

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
│   ├── index.md                      # 菜品与食材分类索引
│   ├── dishes/                       # 单道菜卡片（77 篇）
│   └── ingredients/                  # 食材挑选与预处理卡片（10 篇）
└── scripts/                          # 辅助脚本
    ├── recipe_matcher.py             # 冰箱配餐引擎
    ├── wiki_search.py                # 菜谱受控检索
    ├── wiki_lint.py                  # 格式与死链巡检
    └── check_ingest_status.py        # 原料消化追踪
```

---

## 🙏 致谢

菜谱步骤与实操经验整理自两位博主公开分享的做饭视频：

* **[@村驴](https://space.bilibili.com/417298480)**
* **[@蔡盛坤 (阿蔡美食雕刻)](https://space.bilibili.com/472102908)**

*注：`raw/` 下的原始文字仅用于个人学习和非营利性整理，版权归原作者所有。*

如果你有其他讲解细致、适合家常复刻的美食博主推荐，欢迎在 [Issues](https://github.com/Investigator13th/recipe-wiki/issues) 里留个主页或视频链接。

---

## 📄 开源协议

本项目使用 [MIT License](LICENSE)。
