# LeetCode AI Workspace

[简体中文](./README.md)

An automated LeetCode workspace built for AI IDEs.

The goal is simple: you only need to say something like "fetch this problem" or "fetch today's daily challenge" in the chat box, and the rest is handled automatically by the `leetcode` skill and the setup script, including fetching the problem statement, generating files in multiple languages, writing the description file to disk, and creating a runnable test scaffold.

## What This Is

This repository packages the LeetCode problem-fetching workflow into a skill that can be called directly by an AI IDE:

- Automatically fetches problems from LeetCode CN
- Automatically generates problem statement markdown files
- Automatically generates multi-language solution templates
- Automatically generates local test scaffolding
- Lets the LLM continue filling in examples, assertions, and edge-case tests from the statement

This is not just a template repository. It is a workflow designed for AI-assisted problem solving.

## Key Highlights

### 1. Real One-Line Problem Fetching

You do not need to manually find the problem ID, copy the statement, create files, or build a test scaffold.

You can simply say something like this in your AI IDE:

```text
Fetch two-sum
Fetch https://leetcode.cn/problems/two-sum/
Fetch today's daily challenge
Generate TypeScript and Python templates for this problem
```

The AI can then call the `leetcode` skill and run the repository script to complete the entire initialization flow automatically.

### 2. LLM-Powered Completion, Not Just Empty Files

The value of this workspace is not just creating folders. It helps the AI keep going and do the useful repetitive work for you:

- Fill in test data from the examples in the statement
- Generate assertion structures
- Keep template style consistent across languages
- Add problem-statement navigation comments automatically
- Put you directly into the "implement and run tests" phase

In other words, the AI is not just fetching the problem. It is removing a whole block of repetitive setup work.

### 3. One Shared Capability Across Multiple AI IDEs

One of the design goals of this workflow is to make the same capability reusable across multiple AI IDEs instead of binding it to one tool only.

Supported directions include:

- `Codex`
- `Claude Code`
- `Antigravity`

The idea is to expose the workflow through skill files and symbolic connection points, so that "fetch problem -> generate templates -> generate test scaffold" becomes a standard reusable capability. From a user's perspective, the experience is:

```text
Ask in chat -> AI recognizes or invokes the leetcode skill -> the repository generates the full file set
```

That makes this repository a general-purpose LeetCode AI workspace rather than a private setup tied to one specific IDE.

## What Gets Generated

Running the workflow generates the following files:

- Shared problem statement file: `descriptions/p<id>-<slug>.md`
- Rust: `rust/src/p<id>_<slug>.rs`
- Python: `python/problems/p<id>_<slug>.py`
- Go: `go/problems/p<id>_<slug>_test.go`
- TypeScript: `typescript/problems/p<id>_<slug>.ts`
- C: `c/problems/p<id>_<slug>.c`
- C++: `cpp/problems/p<id>_<slug>.cpp`

Each language template comes with a local test scaffold by default:

- Rust: `rstest` and assertion templates
- Python: parameterized `pytest` templates
- Go: `testing`-based test templates
- TypeScript: `vitest` test templates
- C / C++: sample assertion scaffolds inside `main`

Generated source files also include a problem-statement location comment so you can jump to `descriptions/*.md` quickly from your IDE.

## Typical Usage

### Option 1: Ask Directly in Your AI IDE

This is the recommended way to use the workspace.

Examples:

```text
Fetch two-sum
Fetch today's daily challenge
Fetch this problem and generate all languages
Fetch longest-substring-without-repeating-characters, but only generate rust and typescript
```

If your AI IDE is connected to this repository's `leetcode` skill, it can directly help you:

1. Fetch problem metadata
2. Generate the description file
3. Generate code templates
4. Generate the test scaffold
5. Continue filling examples or even implement the solution if you ask

### Option 2: Use a Config File for Defaults

If you want the script to automatically use a default description language and default programming languages on every run, create a `leetcode.config.json` file in the repository root:

```json
{
  "default_description_language": "zh",
  "default_languages": ["rust"]
}
```

Config fields:

- `default_description_language`: the default language for generated problem statements, supports `zh` and `en`
- `default_languages`: the default programming languages to generate, either as a single string or an array

Example:

```json
{
  "default_description_language": "en",
  "default_languages": ["typescript", "python"]
}
```

With that config, the script will generate English problem statements and `TypeScript + Python` templates by default when no extra CLI arguments are provided.

### Option 3: Run the Script Manually

Command-line arguments override the defaults from the config file.

You can also use the workflow directly from the command line:

```bash
# Fetch a specific problem by slug or URL
python3 .agents/skills/leetcode/setup_problem.py two-sum
python3 .agents/skills/leetcode/setup_problem.py https://leetcode.cn/problems/two-sum/

# Fetch today's daily challenge
python3 .agents/skills/leetcode/setup_problem.py --daily

# Generate specific languages
python3 .agents/skills/leetcode/setup_problem.py two-sum --lang rust --lang python

# Override the description language
python3 .agents/skills/leetcode/setup_problem.py two-sum --description-lang en

# Generate all supported languages
python3 .agents/skills/leetcode/setup_problem.py two-sum --all-langs
```

## Repository Layout

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

## Test Commands

Each language can be tested with its default local toolchain.

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

## IDE and Plugin Recommendations

If you want a smoother experience with clickable test buttons, quick problem-statement navigation, and convenient debugging, it is worth installing the right plugins. The workspace feels much more complete when those pieces are in place.

### Language Plugins vs. Test Plugins

For some languages, most of the testing experience comes from the language plugin itself. For others, a dedicated testing plugin is still helpful.

- Rust: install `rust-analyzer`. Navigation, diagnostics, and most test entry points are typically provided directly by the Rust plugin.
- Python: install the official Python extension. `pytest` discovery and execution are usually integrated there.
- Go: install the official Go extension. Test running and debugging are typically built into the Go plugin.
- C / C++: install the `C/C++` extension. Compilation, debugging, and navigation mainly depend on the language plugin itself.
- TypeScript: language support may come from built-in editor support, but `Vitest` test buttons and a better testing panel experience usually require the dedicated `Vitest` extension.

If TypeScript is one of your main languages here, the `Vitest` extension is very much worth installing because the TypeScript templates in this repository are generated around a `vitest` workflow.

### Recommended Extensions

- `rust-lang.rust-analyzer`
- `ms-python.python`
- `golang.go`
- `ms-vscode.cpptools`
- `vitest-dev.vscode-vitest`
- `open file`

### Quick Jump to the Problem Statement

Generated source files include a statement-location comment pointing to `descriptions/p<id>-<slug>.md`.

It is recommended to install the `open file` extension. Once installed, hover over the path inside that location comment and press `Alt+P` to open the corresponding problem statement file quickly.

This is especially convenient while solving problems, because you can move between code and the statement without manually browsing the directory tree.

### Quick Switch from Run to Debug

In many editors, the default test CodeLens or test button runs the test normally when clicked.

A very useful trick is that if you hold `Alt`, the test button will often switch temporarily into its debug version. Click it in that state and you can jump straight into debugging.

This is especially helpful when you want to inspect variables step by step, verify recursion state, or debug edge cases in pointer-based logic.

## Recommended Workflow

A very smooth working rhythm usually looks like this:

1. Ask the AI to fetch a problem in chat
2. Ask the AI to fill in example-based tests from the statement
3. Implement the solution
4. Run local tests
5. Ask the AI to add edge cases, refactor, or explain the approach if needed

The whole point of this setup is to automate the repetitive and error-prone preparation work so that both you and the AI can focus on the actual algorithm.
