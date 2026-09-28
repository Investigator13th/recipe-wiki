# 🍳 Smart Recipe Wiki | 个人与家庭专属智能食谱知识库

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Status: Active](https://img.shields.io/badge/Dishes-77%20Active-brightgreen.svg)](wiki/index.md)

面向真实个人与家庭生活场景的**模块化食谱 Wiki 与智能配餐知识库**。基于“原子化单菜架构”与“主客观双轨分工”，专注于解决核心日常痛点：

> **“输入冰箱现存食材 ➔ 动态推荐 X 菜 X 汤黄金搭配 ➔ 自动计算最小补料买菜清单”**

---

## 📢 最新更新与待消化原料说明 (Latest Updates)

### 📅 2026-09-28 更新动态
* **首期完成 77 道原子化单菜卡片 Ingest 编译与健康入库**：涵盖硬荤大菜（17道）、半荤海味小炒（17道）、清口时蔬（19道）、养生靓汤与炖盅（17道）以及凉菜点心（7道），健康巡检达成 **0 死链、0 孤儿、0 规范缺陷**。
* **原始素材蓄水池现状**：
  * 在 `raw/` 目录下，尚有 **450 篇** 优质原始做饭视频字幕与剪藏正在排队待消化：
    * `raw/阿蔡/`：已消化 16 篇，**122 篇待消化**
    * `raw/村驴/`：**328 篇全量待消化**
  * 后续将持续按批次增量编译入库，并在此过程中动态增量扩展食材同义词库。

---

## 🌟 项目核心价值与痛点解决

### 1. 告别“死板套餐”，实现“原子单菜组合”
* **传统痛点**：传统菜谱软件或视频多为不可拆分的死板大菜单（如“某期四菜一汤”绑定在一起），只要缺少一种主料就无法复刻；
* **原子架构**：本知识库将所有 raw 素材拆解编译为单道菜标准卡片（存入 `wiki/dishes/<菜名>.md`）。每道菜拥有独立的食材分层（核心主料 / 增味配料 / 常备调料）、精准备料烹饪耗时及 50~100 字决策 Abstract，支持随心自由拼装。

### 2. 冰箱食材反向配餐引擎与极简补料
* **动态配餐**：只需输入冰箱里的剩余食材（例如：“鸡蛋、丝瓜、五花肉”），配餐引擎自动从知识库中组合出营养均衡的 2~4 菜 1 汤；
* **极简补料清单**：明确区分“必须买的核心主料”与“可选增味辅料”，绝不拿油盐酱醋、葱姜蒜等日常常备调料为用户买菜添堵。

### 3. 数据驱动的食材同义词与平替泛化
* 传统文本搜索极易受方言称谓限制（如“西葫芦”搜不到“小瓜”，“冬笋”匹配不到“鲜笋”）；
* 知识库通过 [references/ingredient_synonyms.json](references/ingredient_synonyms.json) 建立方言同义词（如`小瓜 ⇄ 西葫芦`、`菜头 ⇄ 白萝卜`、`海蛎 ⇄ 生蚝`）与同族平替体系（如`龙骨/大骨/扇骨 ⇄ 排骨`、`整鸭/鸭腿 ⇄ 鸭肉`），实现智能跨地域泛化匹对。

### 4. 极简零依赖工具链
* 全套工具（配餐引擎、三层渐进式受控检索、质量巡检、原料消化追踪）**100% 使用 Python 原生标准库编写**；
* 无需安装任何臃肿的第三方依赖，开箱即用，轻量极速。

---

## 🚀 快速上手与使用方式

### 方式一：作为 Skill 装载进 AI 智能体（推荐：WorkBuddy / Antigravity）

本项目根目录已内置标准 [SKILL.md](SKILL.md) 契约，支持作为 Skill 直接装载到 **WorkBuddy**、**Antigravity** 或各类 AI 编程/个人助理中。

#### 装载方式：
1. **直接作为 Skill 目录引入**：
   将本仓库直接克隆或链接至智能体的 `skills/` 自定义技能目录下（如 `skills/recipe/`）；
2. **在对话中自然交互**：
   * 🗣️ *“我冰箱里还剩 2 根丝瓜、几个鸡蛋和一些五花肉，帮我搭配一个 2 菜 1 汤，并告诉我缺什么食材要买。”*
   * 🗣️ *“今晚想吃水煮肉片，帮我调出详细做法和关键火候技巧。”*
   * 🗣️ *“帮我巡检一下当前食谱知识库的健康状态。”*

---

### 方式二：本地命令行脚本直接调用

如果你希望在本地终端直接使用，项目提供了纯 Python 命令行工具：

#### 1. 冰箱食材反查与配餐 (`/match`)
```bash
# 输入手头食材，指定生成 3 道菜的组合方案
python scripts/recipe_matcher.py --ingredients "鸡蛋,丝瓜,五花肉" --count 3
```

#### 2. 三层受控检索 (`/search`)
```bash
# Layer 1: 查看知识库全景大纲分类
python scripts/wiki_search.py --overview

# Layer 2: 检索指定食材/菜品的高密度摘要（避免上下文爆炸）
python scripts/wiki_search.py --search "牛肉"

# Layer 3: 精确加载单道菜完整烹饪步骤
python scripts/wiki_search.py --load "wiki/dishes/水煮肉片.md"
```

#### 3. 原料 Ingest 消化进度追踪
自动比对已落盘菜谱与原始素材，展示当前已消化比例与下一批建议候选：
```bash
python scripts/check_ingest_status.py
```

#### 4. 知识库健康巡检 (`/lint`)
全面检测死链、孤立卡片与 Frontmatter 规范性：
```bash
python scripts/wiki_lint.py
```

---

## 📂 知识库架构契约

```text
recipe/
├── SKILL.md                          # AI 智能体 Skill 定义契约
├── AGENTS.md                         # 知识库运行时规范与操作 SOP
├── README.md                         # 项目总览文档
├── references/
│   └── ingredient_synonyms.json     # 食材同义词与平替族群字典
├── raw/                              # 只读原始语料（博主视频字幕、网页剪藏）
│   ├── 阿蔡/                         # 阿蔡四菜一汤字幕语料库
│   └── 村驴/                         # 村驴做饭视频字幕语料库
├── wiki/                             # 客观知识网络（AI 主权维护）
│   ├── index.md                      # 菜品全景总览与分类大纲
│   └── dishes/                       # 原子单菜卡片库（77+ 道标准化单菜）
│       ├── 红烧肉.md
│       ├── 水煮肉片.md
│       ├── 经典啤酒鸭.md
│       └── ...
├── thoughts/                         # 主观心智流（人类绝对主权，已被 .gitignore 保护）
│   └── notes/                        # 个人口味反馈、咸淡反思、试菜心得
└── scripts/                          # 极简标准库脚本工具集
    ├── recipe_matcher.py             # 冰箱食材智能配餐引擎
    ├── wiki_search.py                # 三层渐进式受控检索引擎
    ├── wiki_lint.py                  # 知识库健康与规范巡检工具
    └── check_ingest_status.py        # 原料消化进度与去重追踪工具
```

---

## 🙏 致谢与鸣谢 (Acknowledgements)

本项目能拥有详实、地道且充满烟火气的做饭步骤与避坑细节，离不开两位优秀美食博主的无私分享。特此诚挚致谢：

* **[@村驴老师](https://space.bilibili.com/417298480)**：感谢村驴老师分享的丰富家庭做饭视频与详实食材实操教程！
* **[@蔡盛坤老师 (阿蔡美食雕刻)](https://space.bilibili.com/472102908)**：感谢阿蔡老师坚持更新的上百期保姆级“四菜一汤”做菜教程与买菜心得！

> *注：本项目中的 `raw/` 资料仅用于个人学习与非营利性知识库整理，菜谱版权与原始创作权归属原作者所有。*

---

## 🤝 美食博主推荐与共建提交 (Contributing & Recommendations)

本项目的目标是打造一个汇聚全网优质家庭烟火气配方、真正好用落地的智能做饭知识库。

如果你有私藏的、讲解详实透彻、适合家庭日常复刻的**宝藏美食博主**（如擅长粤菜煲汤、川湘小炒、鲁菜面点、快手减脂餐等）：
* 欢迎前往 GitHub 仓库提交 [Issues](https://github.com/Investigator13th/recipe-wiki/issues) 推荐博主主页链接或代表作视频；
* 欢迎直接发起 [Pull Requests](https://github.com/Investigator13th/recipe-wiki/pulls)，将处理好的视频字幕或结构化菜谱提交至 `raw/` 或 `wiki/dishes/`；
* 让我们一起把这个个人生活食谱库共建为一个更懂家庭厨房的实用开源神器！

---

## 📄 开源许可证

本项目基于 [MIT License](LICENSE) 开源发布。
