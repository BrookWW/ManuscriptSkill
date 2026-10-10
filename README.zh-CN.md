# ManuscriptSkill

[English](README.md) | [简体中文](README.zh-CN.md)

[![Validation](https://github.com/BrookWW/ManuscriptSkill/actions/workflows/ci.yml/badge.svg)](https://github.com/BrookWW/ManuscriptSkill/actions/workflows/ci.yml)

在 Codex 中用一个可复用技能审阅、修订数学 LaTeX 论文。每轮保存完整源文件副本、独立报告和简短交接记录。支持全文审阅，也支持先规划分段，再为每个块开新聊天逐块审阅。

ManuscriptSkill 面向 GPT-6 级别的 Codex 模型设计。模型和推理强度由你在客户端中选择，技能不指定或强制切换模型。安装内容只有指令和参考文件，不需要运行脚本、Python 服务或 Linux。文献检索、PDF 阅读、编译及子智能体复核取决于当前 Codex 环境可用的工具。

主入口集中说明范围、学术约束和完成条件，分段说明及可选作者风格按需读取，明确要求以用户指令为先。这些设计依据 [GPT-6 官方指令遵循建议](https://developers.openai.com/api/docs/guides/latest-model#instruction-following)，不代表已经测得准确率提升。

[审阅技能](mathematical-manuscript-review/SKILL.md)涵盖数学推理、论证修复、定理表述、文献核验和论文写作，并保留作者的研究目标和论文语言。默认保留现有写作要求和期刊格式。附带的[作者写作偏好](mathematical-manuscript-review/references/personal-style.md)及 [LaTeX 模板](mathematical-manuscript-review/assets/tex_template.tex)是可选的 BrookWW 风格方案，仅在明确要求“采用附带作者写作偏好”时启用；作者要求和提供的期刊模板优先。这些偏好不代表期刊官方规定。

## 安装

在 Codex 中让技能安装器安装本仓库中的技能目录：

```text
使用 $skill-installer 安装以下目录中的技能：
https://github.com/BrookWW/ManuscriptSkill/tree/main/mathematical-manuscript-review
完整安装目录，包括 references、assets 和 agents。
若已安装同名技能，先比较版本，再决定是否替换。
告诉我实际安装位置，以及如何在新聊天中调用。
```

当前 [Codex 技能文档](https://learn.chatgpt.com/docs/build-skills)给出的个人技能目录是 `~/.agents/skills/`。部分已有客户端和安装器使用 `~/.codex/skills/`。以你的安装器和实际技能发现目录为准，同时在两个目录安装同名技能可能造成歧义。

也可以克隆或下载仓库：

```sh
git clone https://github.com/BrookWW/ManuscriptSkill.git
cd ManuscriptSkill
```

将整个 `mathematical-manuscript-review/` 文件夹复制到客户端确认的技能目录。不能只复制 `SKILL.md`，也不要合并覆盖已有版本。若未出现技能，重启 Codex 并核对技能发现目录。

安装前也能试用：让 Codex 读取本地 `mathematical-manuscript-review/SKILL.md` 及其引用文件，再给出审阅请求。安装后用 `$mathematical-manuscript-review` 调用。

## 准备论文

告诉 Codex 项目根目录、入口文件相对于根目录的路径，以及自动查找引用可能遗漏的必要资源。提供 TeX/Bib 源文件、图片、本地类文件和样式，以及判断论文主张所需的计算证据。入口若为 `paper/main.tex`，后续轮次也应保留这个相对路径。Windows 下可使用带盘符的绝对根目录和输出路径，入口及资源路径仍相对于项目。

每轮使用一个位于输入目录之外的新输出目录。Codex 先复制完整的必要项目，再修改副本，以便保留原稿和已有版本。旧审阅报告、凭据、智能体状态和编译缓存不进入稿件副本。必要的外部依赖或链接目标必须明确识别，并在授权范围内复制为真实文件。

以下只是目录示例，仓库不附带这些审阅结果：

```text
paper-original/
  paper/main.tex
  bibliography/references.bib
  figures/
paper-reviews/
  full-001/
    manuscript/              交给下一轮的完整可编辑项目
      paper/main.tex
      bibliography/references.bib
      figures/
    report.md                问题、修改和实际完成的检查
    handoff.json             交付状态与源文件位置
    .audit-work/             可选临时材料
  planning-001/review-plan.md
  pass-001-block-001/
  pass-001-block-002/
  final-full-001/
```

交付内容是源文件和必要资源。编译出的论文 PDF 用于临时检查；作为图片或证据的输入 PDF 按需保留。

## 全文审阅

在 Codex 新聊天中替换占位文字后发送：

```text
使用 $mathematical-manuscript-review，执行一轮 full 全文审阅、修订和复查。
输入项目根目录：<当前完整稿件项目的绝对路径>
入口文件：<相对项目根目录的路径，例如 paper/main.tex>
输出轮次目录：<新的绝对路径，例如 paper-reviews/full-001>
额外必要资源：<相对项目根目录的路径，或“无”>
报告使用中文，论文保持原语言。

修改前，将完整必要项目复制到 manuscript/。
在 manuscript/ 外保存 report.md 和 handoff.json。
只执行这一轮，不读取旧审阅报告或其他聊天。
```

继续之前，阅读报告并检查交接记录。`complete` 表示本轮请求和源文件交付已完成；数学问题仍可能未解决，必须在报告中说明。轮次完成不证明论文正确或达到发表标准。

下一轮另开新聊天，将上一轮已完成的 `manuscript/` 作为输入根目录，保留实际入口相对路径和必要资源路径，并换一个新输出目录。下一轮通常只接收最新完整稿件、当前请求和仍然需要的证据，不接收旧报告或聊天记录。

轮次目录就是文件归档。你可以归档聊天来整理侧边栏，但这不会删除文件、清除记忆或限制访问。新聊天是审阅流程约定，不能建立文件系统隔离。即使本轮没有修改，也应交付完整稿件副本和报告。

## 分段审阅

一遍分段审阅先生成计划，再逐块传递最新完整稿件。规划不计入审阅轮数。

### 生成计划

新开聊天：

```text
使用 $mathematical-manuscript-review 的 segmented 模式，只做规划。
项目根目录：<最新完整稿件项目的绝对路径>
入口文件：<实际入口相对路径>
计划保存位置：<新规划目录>/review-plan.md
计划使用中文，论文保持原语言。

通读完整论文，将实质性论证和附录划分为编号的审阅块，明确范围和顺序。
只生成计划，不修改源文件，不开始逐块审阅。
```

开始审阅前检查计划并记下块数，同一遍中保持计划不变。

### 审阅一个块

每个块各开一个新聊天：

```text
使用 $mathematical-manuscript-review，执行 segmented 模式的一块审阅。
输入项目根目录：<最新完整稿件项目的绝对路径>
入口文件：<实际入口相对路径>
固定计划：<review-plan.md 的绝对路径>
本轮审阅块：第 1 块
输出轮次目录：<新的绝对路径，例如 pass-001-block-001>
额外必要资源：<相对路径，或“无”>
报告使用中文，论文保持原语言。

先复制完整必要项目，再审阅指定块。
按需查阅其他段落，并修复直接受影响的内容。
交付完整 manuscript/、report.md 和 handoff.json。
只做这一块，不读取旧审阅报告。
```

第二块使用第一块交付的 `manuscript/`，沿用同一计划，增加块编号并选择新输出目录。依次传递到最后一块。若所有块都从同一份初稿开始，前面块的修改就无法累积。

下一遍需根据最新完整稿件重新规划。最终全文复查需要另行请求。完整约定见[分段模式说明](mathematical-manuscript-review/references/segmented-review.md)和[轮次操作指南](mathematical-manuscript-review/references/manual-workflow.md)。

## 多轮组合与恢复

模式可以组合，例如：

| 阶段 | 聊天安排 | 输入 |
|---|---|---|
| 三轮全文审阅 | 每轮新开聊天 | 原稿，随后逐轮使用最新完整版本 |
| 一次分段规划 | 新开规划聊天 | 第三轮完整版本 |
| 一遍分段审阅 | 每块新开聊天 | 最新版本和固定计划 |
| 一轮最终全文审阅 | 新开聊天 | 最后一个块的完整版本 |

若计划有 N 个块，此示例共用 N+5 个聊天，其中一个只做规划。轮数可以调整；没有实验表明这个安排能获得最优质量或最低费用。技能可以执行更长的任务，但本流程在每次交接后停下，由你控制下一轮输入和范围。

审阅中断或必要源文件依赖缺失时，保留部分输出，从最后完整交付的稿件出发，在新目录重试。不要把 `incomplete` 的交接记录当成已完成版本。若要抢救部分结果，可以明确要求 Codex 使用它，并注明这是不完整输入。尚未解决的数学问题应写入报告，不一定使已完成的审阅流程变成未完成。

报告必须区分实际执行、不可用和失败的检查。未读到的文献仍然未经核验。没有子智能体工具时可以直接审阅，TeX 编译也是可选检查；多人一致和编译成功都不能证明数学正确。

## 与 ManuscriptAgent 的关系

本技能源自 [ManuscriptAgent](https://github.com/BrookWW/BrookWW-ManuscriptAgent)，保留审阅方法和源文件交接，由你在 Codex 中管理轮次。

| 能力 | ManuscriptSkill | ManuscriptAgent 执行器 |
|---|---|---|
| 数学审阅指令 | 独立技能 | 执行器内置技能 |
| 轮次衔接 | 用户开新聊天并指定输入 | 执行器调度会话和版本 |
| 运行环境 | 能读写文件的客户端及工具 | 满足原项目要求的 macOS 环境 |
| 隔离 | 客户端权限和流程约定 | 执行器实施沙箱及访问限制 |
| 凭据、网络和进程清理 | 客户端控制 | 执行器提供专门控制 |
| 审阅结果 | 完整源文件、报告和交接记录 | 完整源文件及运行记录 |

ManuscriptSkill 不提供内核沙箱、自动调度、独立凭据、网络白名单或可靠的进程清理机制。实际行为受客户端权限、项目指令、可访问文件和模型选择影响。没有对照研究证明它与执行器审阅质量相同，也不能保证 GPT-6 级别模型一定带来优势。

## 开发与验证

安装后的技能没有包依赖。仓库检查使用 Python 3.11+ 和 PyYAML，均为开发工具：

```sh
python -m pip install -r requirements-dev.txt
python scripts/validate.py
python -m unittest discover -s tests -v
```

若系统将 Python 3 命名为 `python3`，使用该命令。还可用 `python scripts/validate.py --round <轮次目录绝对路径>` 检查交付轮次；它检查交接记录和文件树，不检查论文数学是否正确。

CI 检查包结构、元数据、引用资源和跨平台测试用例。这些检查覆盖打包和流程约定，不评估研究级数学可靠性，也不能证明模型会遵守每条指令。真实论文评估需用所选模型和工具另行运行，再由人判断发现和修改是否成立。仓库不应提交私有论文、生成的审阅归档或认证材料。

[验证记录](docs/validation.md)记载了本次审计和小规模行为试跑。[合成测试稿](examples/regularity/README.md)故意包含缺陷，可用来复现基本流程检查。

## 仓库结构

```text
mathematical-manuscript-review/
  SKILL.md
  agents/openai.yaml
  references/
    manual-workflow.md
    segmented-review.md
    personal-style.md
  assets/tex_template.tex
README.md
README.zh-CN.md
```

## 许可证

[MIT](LICENSE)。
