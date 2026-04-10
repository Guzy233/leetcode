# LeetCode AI Workspace

[English](./README.en.md)

一个给 AI IDE 准备的 LeetCode 自动化工作区。

核心目标很简单：你只需要在对话框里说一句“拉取某道题”或“拉取今日每日一题”，剩下的事情交给 `leetcode skill` 和脚本自动完成，包括抓取题面、生成多语言文件、落盘描述文件，以及补好可直接运行的测试脚手架。

## 这是什么

这个仓库把 LeetCode 拉题流程封装成了一套可被 AI IDE 直接调用的 skill：

- 自动拉取 LeetCode CN 题目
- 自动生成题面 markdown
- 自动生成多语言题解模板
- 自动生成本地测试框架
- 支持 LLM 继续基于题面补全样例、断言和边界测试

它不是单纯的“代码模板仓库”，而是一套面向 AI 协作的刷题工作流。

## 最大亮点

### 1. 真正的一句话拉题

你不需要手动找题号、复制题面、创建文件、搭测试框架。

只要在 AI IDE 对话框里说：

```text
拉取 two-sum
拉取 https://leetcode.cn/problems/two-sum/
拉取今天每日一题
帮我生成这道题的 TypeScript 和 Python 模板
```

AI 就可以通过 `leetcode skill` 调用本仓库脚本，自动完成整套初始化。

### 2. LLM 智能补全，不只生成空文件

这个工作区的重点不是“建个文件夹”，而是让 AI 继续往下做真正有价值的工作：

- 根据题面示例补全测试数据
- 生成断言结构
- 保持各语言模板风格统一
- 自动附带题面跳转注释
- 让你直接进入“写解法并跑测试”的状态

也就是说，AI 不只是帮你拉题，而是把一整段重复劳动吃掉。

### 3. 多种 AI IDE 可复用同一套能力

当前工作流的设计重点之一，就是让同一套能力可以接入不同 AI IDE，而不是绑定某一个工具。

支持思路包括：

- `Codex`
- `Claude Code`
- `Antigravity`

实现方式是通过 skill 文件和符号化连接入口，把“拉题 -> 生成模板 -> 生成测试脚手架”的动作封装成标准能力。对于使用者来说，体验就是：

```text
在对话框里提出需求 -> AI 识别/调用 leetcode skill -> 仓库自动生成完整文件
```

这意味着你可以把这个仓库当作一个通用的 LeetCode AI 工作台，而不只是某个 IDE 的私有配置。

## 自动生成内容

执行后会生成这些内容：

- 共享题面文件：`descriptions/p<id>-<slug>.md`
- Rust：`rust/src/p<id>_<slug>.rs`
- Python：`python/problems/p<id>_<slug>.py`
- Go：`go/problems/p<id>_<slug>_test.go`
- TypeScript：`typescript/problems/p<id>_<slug>.ts`
- C：`c/problems/p<id>_<slug>.c`
- C++：`cpp/problems/p<id>_<slug>.cpp`

其中各语言模板默认自带本地测试骨架：

- Rust：`rstest` / 断言模板
- Python：`pytest` 参数化模板
- Go：`testing` 测试模板
- TypeScript：`vitest` 测试模板
- C / C++：`main` 中的样例断言骨架

生成后的源文件还会附带题面文件定位注释，方便在 IDE 中快速跳转到 `descriptions/*.md`。

## 典型使用方式

### 方式一：在 AI IDE 中直接说

这是最推荐的使用方式。

示例：

```text
拉取 two-sum
拉取今日每日一题
拉取这道题并生成全部语言
拉取 longest-substring-without-repeating-characters，只生成 rust 和 typescript
```

如果当前 AI IDE 已接入本仓库的 `leetcode skill`，它就可以直接帮你完成：

1. 抓取题目信息
2. 生成描述文件
3. 生成代码模板
4. 生成测试脚手架
5. 继续按你的要求补充样例或直接实现题解

### 方式二：通过配置文件设置默认值

如果你希望脚本在每次运行时自动使用固定的描述语言和默认编程语言，可以在仓库根目录创建 `leetcode.config.json`：

```json
{
  "default_description_language": "zh",
  "default_languages": ["rust"]
}
```

配置项说明：

- `default_description_language`：描述文件默认语言，支持 `zh` 和 `en`
- `default_languages`：默认生成的编程语言，可以是单个字符串，也可以是数组

示例：

```json
{
  "default_description_language": "en",
  "default_languages": ["typescript", "python"]
}
```

这样在不额外传参时，脚本就会默认生成英文题面，以及 `TypeScript + Python` 模板。

### 方式三：手动运行脚本

命令行参数会覆盖配置文件中的默认值。

如果你想直接在命令行使用，也可以执行：

```bash
# 拉取指定题目（slug 或 URL）
python3 .agents/skills/leetcode/setup_problem.py two-sum
python3 .agents/skills/leetcode/setup_problem.py https://leetcode.cn/problems/two-sum/

# 拉取每日一题
python3 .agents/skills/leetcode/setup_problem.py --daily

# 指定语言
python3 .agents/skills/leetcode/setup_problem.py two-sum --lang rust --lang python

# 覆盖描述语言
python3 .agents/skills/leetcode/setup_problem.py two-sum --description-lang en

# 生成全部支持语言
python3 .agents/skills/leetcode/setup_problem.py two-sum --all-langs
```

## 仓库结构

```text
.
├── .agents/skills/leetcode/setup_problem.py
├── descriptions/
├── rust/src/
├── python/problems/
├── go/problems/
├── typescript/problems/
├── c/problems/
└── cpp/problems/
```

## 测试命令

不同语言可以直接用各自目录里的默认工具运行测试。

### Rust

```bash
cd rust
cargo test
```

### Python

```bash
pytest -q python/problems/p<id>_<slug>.py
```

### Go

```bash
cd go
go test ./problems -run Test_ -v
```

### TypeScript

```bash
cd typescript
npm test -- --run problems/p<id>_<slug>.ts
```

### C

```bash
gcc -std=c11 -O2 -Wall c/problems/p<id>_<slug>.c -o /tmp/lc_c && /tmp/lc_c
```

### C++

```bash
g++ -std=c++20 -O2 -Wall cpp/problems/p<id>_<slug>.cpp -o /tmp/lc_cpp && /tmp/lc_cpp
```

## IDE 与插件建议

如果你希望在编辑器里直接点测试按钮、快速跳转题面、顺手调试，建议把插件装齐。这个仓库的体验会明显更完整。

### 语言插件与测试插件

有些语言的测试体验主要来自语言插件本身，有些则需要额外安装独立测试插件。

- Rust：建议安装 `rust-analyzer`。代码跳转、诊断和大部分测试入口通常由 Rust 插件直接提供。
- Python：建议安装 Python 官方插件。`pytest` 的测试发现和运行通常由 Python 插件集成提供。
- Go：建议安装 Go 官方插件。测试运行、调试入口通常由 Go 插件直接提供。
- C / C++：建议安装 `C/C++` 插件。编译、调试和跳转主要依赖语言插件本身。
- TypeScript：语言支持可由 TypeScript 自带能力或编辑器内置能力提供，但 `Vitest` 测试按钮和更好的测试面板体验通常需要额外安装 `Vitest` 插件。

如果你主要刷 `TypeScript`，`Vitest` 插件基本是值得单独安装的，因为本仓库的 TypeScript 模板就是按 `vitest` 工作流生成的。

### 推荐安装

- `rust-lang.rust-analyzer`
- `ms-python.python`
- `golang.go`
- `ms-vscode.cpptools`
- `vitest-dev.vscode-vitest`
- `open file`

### 快速跳转到题面

生成后的源码文件会带一段题面定位注释，指向 `descriptions/p<id>-<slug>.md`。

建议安装 `open file` 插件。安装后，把光标悬停在这类定位注释里的路径上，按 `Alt+P`，就可以快速打开对应题面文件。

### 一键切换到调试测试

很多编辑器里的测试 CodeLens / 测试按钮，在默认状态下点击是“运行测试”。

一个很实用的小技巧是：按住 `Alt` 时，测试按钮通常会临时切换成“调试测试”版本。这时直接点击，就能更快进入调试流程。


## 推荐工作流

一个非常顺手的节奏通常是这样：

1. 在对话框里让 AI 拉取题目
2. 让 AI 根据题面自动补齐样例测试
3. 开始实现解法
4. 跑本地测试
5. 再让 AI 帮你补边界 case、重构或解释思路

这套流程的意义是，把重复、机械、容易出错的准备工作自动化，让人和 AI 都把精力放在真正的算法实现上。

## License

本项目采用 MIT License。详见 [LICENSE](./LICENSE)。
