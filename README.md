<div align="center">

# 简历一条龙：resume.skill

### 整理经历、生成简历、模拟面试追问、回改简历定稿

适用于 Claude Code、Codex 和其他可读取 `SKILL.md`、运行本地脚本的 AI Agent。<br>
中文排版优化，本地离线渲染。

<img src="https://img.shields.io/badge/Agent%20Skill-SKILL.md-5A4FCF?style=flat-square">
<img src="https://img.shields.io/badge/Runtime-Claude%20Code%20%7C%20Codex-7B61FF?style=flat-square">
<img src="https://img.shields.io/badge/Input-Chat%20%7C%20Resume%20%7C%20Docs-0FA36B?style=flat-square">
<img src="https://img.shields.io/badge/Output-DOCX%20%7C%20PDF%20%7C%20MD%20%7C%20TXT-1E88E5?style=flat-square">
<img src="https://img.shields.io/badge/Chain-interview.skill-E8590C?style=flat-square">
<img src="https://img.shields.io/badge/License-MIT-4C9A2A?style=flat-square">

**经历采集 · 贡献拆分 · STAR 改写 · JD 定向修改 · 数字来源分级 · 内容体检 · 经历库复用 · 多格式导出**

[核心特色](#核心特色) · [先看一个例子](#先看一个例子) · [处理流程](#处理流程) · [安装](#安装) · [使用](#使用) · [输出文件](#输出文件) · [衔接模拟面试](#衔接模拟面试)

</div>

---

## 核心特色

- **只写你说过的内容**：每条简历内容对应你讲过的具体经历，不补充你没有提供的数字
- **数字按来源分级**：你测量过的、你记不清怎么得来的、只有覆盖范围没有比例的、完全没有的，四类分别用不同写法
- **区分个人贡献与团队贡献**：回答中出现"我们"时会追问其中哪部分由你完成
- **内容体检**：为每条要点生成面试可能追问的问题，答不上来的标出并给出改法
- **从经历到成品**：对话采集、内容改写、JD 匹配、文件导出形成完整流程
- **对话式经历采集**：依次追问场景、你的动作、当时的判断、结果和量化，五项问完再进入下一段经历
- **STAR / XYZ 改写**：把职责描述改成有动作、有规模、有结果的简历要点
- **JD 定向匹配**：提取岗位关键词，分析命中项与缺失项，调整内容顺序和表达
- **按阅读顺序排版**：把最能匹配岗位的内容放在 HR 最先看到的位置
- **多种输入方式**：支持对话、旧简历、项目报告与绩效自评，三种可叠加
- **多场景适配**：支持校招、社招、转行，以及产品、运营、数据、技术等岗位侧重
- **经历库可复用**：经历采集一次后存为本地文件，投递新岗位只需提供新的 JD
- **多格式导出**：DOCX、PDF、Markdown 与纯文本，纯文本用于 BOSS 直聘等平台直接粘贴
- **离线稳定渲染**：中文字体随包提供，不依赖在线服务，PDF 文本可搜索、可复制
- **隐私默认收敛**：身份证号、家庭住址等敏感字段默认不进入简历正文
- **可衔接模拟面试**：与 `interview.skill` 共用经历库，简历定稿后直接进入面试演练

---

## 先看一个例子

同一段原始经历，两种处理方式。

> 你说的是：「用 Qwen + LoRA 做了个问答系统，效果还行。」

**常见做法**

```
基于 Qwen + LoRA 完成领域微调，结合 RAG 检索增强，
将问答召回率提升至 92%
```

92% 是补上去的。你没说过这个数字，面试时也解释不了它怎么来的。

**这个 skill 的做法**

```
基于 Qwen + LoRA 完成领域微调，结合 RAG 检索增强

[需你补充] 召回率提升了多少？你测过吗？基线是哪个版本？
           —— 说不清就不写数字，改成「完成 XX 场景问答能力落地」
```

数字要么有来源，要么不写。这个判断在流程里执行，不靠模型自觉。

---

## 处理流程

```
     经历采集
  对话 / 旧简历 / 项目材料
          │
          ▼
      profile.md              全量经历，不做取舍、不做润色
          │
          ├─────── 内容审查 ──── 无来源的数字剥离，缺失项退回补充
          │
          ▼
      JD 定向匹配              命中项、缺失项、内容顺序
          │
          ▼
      改写与排版               只在审查通过的内容里操作
          │
          ▼
      内容体检                 逐条生成面试追问，答不上来的回改
          │
          ▼
  简历 + 修改说明 + 差距清单 + 追问清单
```

换一个岗位时，从 `profile.md` 往下重跑，不需要重新采集经历。

---

## 适合谁

- 转行、跨专业，不确定过往经历怎么对应到目标岗位
- 有旧简历，想按具体 JD 改一版，但每次改都接近重写
- 简历投出去没有回音，不确定问题在内容还是在排版
- 同时投多个方向，不想每次从头讲一遍自己的经历
- 担心简历写得过满，面试时接不住追问

---

## 安装

仓库自带 `.claude/skills/resume-skill/` 完整 skill 目录（SKILL.md、profile-schema.md、scripts/、schema/、assets/ 一体）。

**Claude Code — 全局，所有项目可用**

```bash
git clone https://github.com/Sean-9/resume.skill.git resume.skill-src
cp -r resume.skill-src/.claude/skills/resume-skill ~/.claude/skills/
```

**Claude Code — 仅当前项目**

```bash
git clone https://github.com/Sean-9/resume.skill.git resume.skill-src
mkdir -p .claude/skills
cp -r resume.skill-src/.claude/skills/resume-skill .claude/skills/
```

**其他 Agent**：把 `.claude/skills/resume-skill/` 整个目录放入对应的 skills 目录——SKILL.md、profile-schema.md、scripts/、schema/、assets/ 要一起，缺了 Phase 6 渲染会断。

**运行依赖**：

```bash
pip install python-docx          # render.py / to_text.py 用
brew install --cask libreoffice  # macOS，to_pdf.sh 用
sudo apt install libreoffice     # Ubuntu，to_pdf.sh 用
```

随包字体在 `assets/`（Noto Sans CJK，`.otf` 或 `.ttc` 均可，脚本自动探测），PDF 离线渲染不缺字。

---

## 使用

新开一个会话，直接说明需求：

```
帮我写一份简历，我是化学背景想转数据岗
```

```
这是我的旧简历和目标 JD，帮我改一版
```

```
我有几份项目报告和绩效自评，帮我整理成简历
```

采集阶段的追问会比预期多。每段经历要问到场景、你的动作、当时的判断、结果和量化五项，问不满不进入下一段。

---

## 输出文件

```
./jobsearch/
├── profile.md                        经历库，全量保存，反复使用
├── jd/
│   └── 某公司_产品经理.md
├── resumes/
│   ├── 某公司_产品经理_20260807.docx
│   ├── 某公司_产品经理_20260807.pdf
│   ├── 某公司_产品经理_20260807.txt        BOSS 直聘等平台粘贴用
│   ├── 某公司_产品经理_20260807_修改说明.md
│   └── 某公司_产品经理_20260807_体检清单.md
└── 台账.md                            投递记录
```

**修改说明**记录每一处改动的依据：

| # | 改前 | 改后 | 依据 |
|---|---|---|---|
| 1 | 负责数据处理相关工作 | 设计配置化字段映射方案，仪器适配周期从 2 天缩短到 10 分钟 | 原句没有动作和结果；补入你确认过基线的数字 |
| 2 | 用户增长提升 30% | 主导 XX 功能上线，覆盖 3 类核心用户 | 30% 无法说明归因，体检未通过，改为覆盖范围表述 |

**体检清单**逐条列出面试可能的追问：

```markdown
## 需重点准备
### 「用户增长提升 30%」
- 这个 30% 怎么计算的？和哪个时间段对比？
- 同期是否有其他因素影响增长？归因依据是什么？
- 建议：答不上来就改成「主导 XX 功能上线，覆盖 X 类用户」，去掉百分比
```

---

## 衔接模拟面试

与 `interview.skill` 共用经历库，简历定稿后可直接进入面试演练。联动 skill 仓库：[Sean-9/MockInterview](https://github.com/Sean-9/MockInterview)（skill 名 `MockInterview.skill`）。

本 skill 启动时自动检查本机是否已安装该联动 skill；未安装则自动拉取：

```bash
git clone https://github.com/Sean-9/MockInterview.git ~/.claude/skills/mockinterview
```

```
resume.skill                          interview.skill
     │                                      │
     ├──► profile.md ──────────────────────►│   行为面命题
     ├──► 体检清单 ────────────────────────►│   追问题库
     └──► JD 解析 ─────────────────────────►│   跳过重复解析
                                            │
                                            ▼
                                        差距报告
                                            │
              ◄─────────────────────────────┘
        答不上来的内容，回到简历修改
```

面试 skill 会优先针对来源不清的数字出题——这类内容在真实面试中最容易出问题。接入方法见 `SKILL.md` 的「与 interview.skill 的联动」一节，改动一处即可。

---

## 隐私

所有文件保存在本地目录，不上传。敏感字段默认不进入简历正文。

---

## License

MIT

<div align="center">

由 [九九渊 / Sean-9](https://github.com/Sean-9) 维护 · 欢迎提 Issue

</div>
