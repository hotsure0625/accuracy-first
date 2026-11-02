# Accuracy First v1.0 — AI 高正确率代码修改系统

**设计目的**：让 AI 先理解、后修改，少改动、多反证、按风险验证，从而提高首次修改成功率并减少重复人工测试。

它不是“零测试保证”，也不会自动接管你的项目、生成生产发布授权或宣称改动绝对正确。

## 包含的能力

- `accuracy-first` Skill：调查 → 不变量 → 风险分级 → 反例推演 → 最小改动 → 对抗审查 → 分级验证。
- `accuracy-critic` Agent：Claude Code 独立上下文只读审查，专找可能的回归和事故条件。
- `inspect_diff.py`：可选只读 Git hygiene 快检；不会修改文件、不运行测试、不代替编译和业务验证。
- `risk-gates.md`、`review-contract.md`：风险分级与交付契约。

## 安装（把 ZIP 解压后选择一种或两种）

### Codex CLI / IDE

把压缩包中的 `.agents/skills/accuracy-first/` 完整复制到目标 Git 项目根目录的 `.agents/skills/accuracy-first/`。
在 Codex 中使用 `$accuracy-first` 选择它，或告诉 Codex“用 accuracy-first 修改这个 Bug”。

Codex 的独立审查：如果环境支持子 Agent，将 `review-contract.md` 连同原始需求和 Diff 交给独立审查会话；**本包的 `.claude/agents/` 文件不是 Codex agent 注册文件**。
不支持子 Agent 时可以另开 Codex 会话，只做只读 Review，再把发现交给主会话；不要把这种情况称为已自动完成独立审查。

### Claude Code

把 `.claude/skills/accuracy-first/` 复制到 Git 项目根目录，
把 `.claude/agents/accuracy-critic.md` 复制到项目对应目录。
然后在 Claude Code 中运行：

```text
/accuracy-first 修复这个 Bug：<具体需求>
```

Skill 会在审查步骤尽可能委托 `accuracy-critic`；若代理工具不可用，必须如实说明并使用独立会话/非独立复核。

## 可选的只读 Git 检查

进入项目根目录，运行（Python 3 标准库即可）：

```bash
python .agents/skills/accuracy-first/scripts/inspect_diff.py
# 或在 Claude Code 项目里
python .claude/skills/accuracy-first/scripts/inspect_diff.py
# 如果要检查相对于已有基线的提交差异（基线必须存在）
python .agents/skills/accuracy-first/scripts/inspect_diff.py --base origin/main
```

脚本运行 `git status`、`git diff --stat`、`git diff --check`（含暂存区）；**不会涵盖未跟踪文件，也不证明功能正确**。

## 建议使用方式

向 AI 提供：问题现象、预期行为、受影响模块、不能更改的内容、可用测试预算。
例如：

> 使用 accuracy-first 修复 [问题]，只准修改 [模块]。先调查并列出不变量，修改时保持最小 Diff。按风险控制测试预算；先做 Git Diff / 静态检查，必要时执行针对性测试。完成后进行独立对抗审查，并标出没验证的部分。不要提交或发布。

## 将来升级

- V1：纯规则 + 只读审查 + 轻量 Git 快检（本包）。
- V2：根据语言/模块动态选择编译器、静态分析器、定向测试命令，自动记录验证证据。
- V3：用历史 Bug 建立对照实验，统计首次通过率、审查发现率、回归率、耗时和修改量，持续优化 Skill。

## 文件结构

```text
accuracy-first-kit/
├── README.md
├── .agents/skills/accuracy-first/         # Codex
│   ├── SKILL.md
│   ├── references/risk-gates.md
│   ├── references/review-contract.md
│   └── scripts/inspect_diff.py
├── .claude/skills/accuracy-first/          # Claude Code
│   ├── SKILL.md
│   ├── references/risk-gates.md
│   ├── references/review-contract.md
│   └── scripts/inspect_diff.py
└── .claude/agents/accuracy-critic.md      # Claude Code 独立子 Agent
```

**安装前请审阅文件和本地安全规范**：不要覆盖已有项目规则，确认权限与相关代码可被允许的 AI 工具访问。对于公司私有仓库，请遵守公司授权及数据安全要求。
