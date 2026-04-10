---
name: leetcode
description: Fetch problems from leetcode.cn and auto-generate multi-language local templates.
user_invocable:
  - leetcode
  - daily
---

# LeetCode Solution Skill

Follow these steps to pull a new problem:

1.  **Setup Scaffold**:
    Run this command to create the problem statement and code template:
    ```bash
    # Fetch a specific problem
    python3 .agents/skills/leetcode/setup_problem.py <slug-or-url>

    # Fetch today's daily challenge
    python3 .agents/skills/leetcode/setup_problem.py --daily

    # Pick one or more languages explicitly
    python3 .agents/skills/leetcode/setup_problem.py <slug-or-url> --lang rust --lang python

    # Generate all supported languages
    python3 .agents/skills/leetcode/setup_problem.py <slug-or-url> --all-langs
    ```
    This step is very straightforward and requires no additional thought, so please proceed immediately.

    Current folder layout:
    - `rust/`: Cargo crate, `src/lib.rs`, `src/p<id>_<slug>.rs`, `src/p<id>_<slug>.md`
    - `python/`: `problems/p<id>_<slug>.py` and matching `.md`（pytest 测试直接写在同一个 `p*.py` 文件）
    - `cpp/`: `problems/p<id>_<slug>.cpp` and matching `.md`
    - `go/`: `problems/p<id>_<slug>.go`、`problems/p<id>_<slug>_test.go`、matching `.md`
    - `typescript/`: `problems/p<id>_<slug>.ts`、`tests/p<id>_<slug>.test.ts`、matching `.md`

2.  **Add Tests**:
    Read the generated problem files for the target language.
    - Python: 在 `python/problems/p<id>_<slug>.py` 里直接补全 `@pytest.mark.parametrize` 测试，不再单独建 `test_*.py`。
    - Go: 在 `go/problems/p<id>_<slug>_test.go` 里补测试。
    - TypeScript: 在 `typescript/tests/p<id>_<slug>.test.ts` 里补测试。
    - If the user is working on Rust:
    - Implement the `#[rstest]` cases in `rust/src/p<id>_<slug>.rs`.
    - **Recommended**: Use `serde_json::from_str` to parse input from strings directly, allowing you to copy-paste test cases directly from LeetCode.
    - Note: Special data types (ListNode, TreeNode) require manual test case construction using appropriate helpers.
    - Always use `pretty_assertions::assert_eq`.
    - **Note**: Done't actually solve the problem.
    - Reply short message after creation.
    - 在 agent 检查阶段，顺手把模板整理成更适合开写的状态。
    - 如果题目输入是二维数组、矩阵、网格，预先补上 `let m = ...; let n = ...;`，优先从入参数组长度获取。
    - 如果题目输入是一维数组且后续明显会频繁使用长度，预先补上长度变量，例如 `let n = nums.len();`；若存在第二个主要数组，也可补 `m`。
    - 对于长度、下标、位移等会参与索引的量，优先在检查阶段转成 `usize`，例如 `let n = nums.len();`、`let k = k as usize;`。
    - 如果题意提到结果需要取模，预先定义 `const MOD: i64 = 1_000_000_007;`；如果题目明确给出其他模数，则使用题目里的值。
