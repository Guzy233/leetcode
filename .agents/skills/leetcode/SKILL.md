---
name: leetcode
description: Fetch problems from leetcode.cn and generate local multi-language templates.
user_invocable:
  - leetcode
  - daily
---

# LeetCode Skill

Use this skill to fetch a LeetCode problem (or daily challenge) and scaffold local files.

## 1. Generate Problem Files

Run one of the following commands:

```bash
# Fetch a specific problem by slug or URL
python3 .agents/skills/leetcode/setup_problem.py <slug-or-url>

# Fetch today's daily challenge
python3 .agents/skills/leetcode/setup_problem.py --daily

# Generate one or more languages explicitly
python3 .agents/skills/leetcode/setup_problem.py <slug-or-url> --lang rust --lang python

# Generate all supported languages
python3 .agents/skills/leetcode/setup_problem.py <slug-or-url> --all-langs

# Override description language for this run
python3 .agents/skills/leetcode/setup_problem.py <slug-or-url> --description-lang en
```

Default behavior:

- If `--lang` is not provided, the script uses the configured default languages.
- If no project config exists, it falls back to the built-in default language selection.
- Command-line arguments override defaults for the current run.

## 2. Current Output Layout

- Shared description file (all languages):
  - `descriptions/p<id>-<slug>.md`
- Rust:
  - `rust/src/p<id>_<slug>.rs`
  - auto-registers `mod p<id>_<slug>;` in `rust/src/lib.rs`
- Python:
  - `python/problems/p<id>_<slug>.py` (includes inline pytest template)
- C++:
  - `cpp/problems/p<id>_<slug>.cpp` (single-file function + `main` test scaffold)
- C:
  - `c/problems/p<id>_<slug>.c` (single-file function + `main` test scaffold)
- Go:
  - `go/problems/p<id>_<slug>_test.go` (single file with function + test scaffold)
- TypeScript:
  - `typescript/problems/p<id>_<slug>.ts` (includes solution scaffold + vitest scaffold in same file)

Every generated source file includes a clickable comment block for the description file in this format:

```text
Problem statement file
"descriptions\\p<id>-<slug>.md"
```

## 3. Test Completion Guidelines

After scaffolding, the assistant must inspect the generated description file and manually fill in examples from the problem statement instead of solving the full problem unless the user asks for a solution.

This step is required even if the generator already created placeholder tests. Do not leave the default placeholder case, parsing comments, or `todo!`/`TODO` test bodies in place when the problem statement provides enough example data to build the test scaffold.

- Rust: complete `#[rstest]` cases in `rust/src/p<id>_<slug>.rs`.
  - Prefer `serde_json::from_str` for fast copy/paste of LeetCode examples.
  - Use helper constructors manually for `ListNode` / `TreeNode` when needed.
  - Keep `pretty_assertions::assert_eq`.
- Python: complete `@pytest.mark.parametrize` directly in `python/problems/p<id>_<slug>.py`.
- Go: complete tests in `go/problems/p<id>_<slug>_test.go`.
- TypeScript: complete tests in `typescript/problems/p<id>_<slug>.ts`.

## 4. Agent Behavior Notes

- Keep responses short after file creation.
- For `daily` / `--daily` requests, fetch first, then immediately inspect the generated files and complete the local test scaffold from the statement examples before replying.
- Treat test completion as assistant work rather than generator work. If the statement contains special structures that are awkward to infer automatically, hand-write the fixture parsing or helper constructors needed for the local tests.
- While checking templates, you may make small ergonomic prep edits (for example, add obvious length variables) only when they are low-risk and clearly useful.
