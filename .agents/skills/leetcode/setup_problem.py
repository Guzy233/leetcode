import argparse
import json
import os
import re
import sys

import requests


DESCRIPTION_DIR = "descriptions"
DEFAULT_REGION = "cn"
DEFAULT_DESCRIPTION_LANGUAGE = "zh"
DEFAULT_PROGRAMMING_LANGUAGES = ["rust"]
DEFAULT_CONFIG_PATHS = [
    "leetcode.config.json",
    os.path.join(".agents", "skills", "leetcode", "config.json"),
]


LANGUAGE_CONFIGS = {
    "rust": {
        "label": "Rust",
        "snippet_slugs": ["rust"],
        "root_dir": "rust",
        "problem_dir": os.path.join("rust", "src"),
        "code_ext": ".rs",
    },
    "python": {
        "label": "Python",
        "snippet_slugs": ["python3", "python"],
        "root_dir": "python",
        "problem_dir": os.path.join("python", "problems"),
        "code_ext": ".py",
    },
    "cpp": {
        "label": "C++",
        "snippet_slugs": ["cpp"],
        "root_dir": "cpp",
        "problem_dir": os.path.join("cpp", "problems"),
        "code_ext": ".cpp",
    },
    "c": {
        "label": "C",
        "snippet_slugs": ["c"],
        "root_dir": "c",
        "problem_dir": os.path.join("c", "problems"),
        "code_ext": ".c",
    },
    "go": {
        "label": "Go",
        "snippet_slugs": ["golang"],
        "root_dir": "go",
        "problem_dir": os.path.join("go", "problems"),
        "code_ext": "_test.go",
    },
    "typescript": {
        "label": "TypeScript",
        "snippet_slugs": ["typescript"],
        "root_dir": "typescript",
        "problem_dir": os.path.join("typescript", "problems"),
        "code_ext": ".ts",
    },
}

DESCRIPTION_LANGUAGE_ALIASES = {
    "zh": "zh",
    "cn": "zh",
    "zh-cn": "zh",
    "zh_cn": "zh",
    "chinese": "zh",
    "en": "en",
    "en-us": "en",
    "en_us": "en",
    "english": "en",
}


def load_config():
    for path in DEFAULT_CONFIG_PATHS:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict):
                raise ValueError(f"Config file must contain a JSON object: {path}")
            return data, path
    return {}, None


def normalize_description_language(raw_value):
    if raw_value is None:
        return DEFAULT_DESCRIPTION_LANGUAGE

    normalized = DESCRIPTION_LANGUAGE_ALIASES.get(str(raw_value).strip().lower())
    if not normalized:
        supported = ", ".join(sorted(set(DESCRIPTION_LANGUAGE_ALIASES.values())))
        raise ValueError(
            f"Unsupported description language '{raw_value}'. Supported values: {supported}"
        )
    return normalized


def normalize_languages(raw_languages):
    if raw_languages is None:
        return list(DEFAULT_PROGRAMMING_LANGUAGES)
    if isinstance(raw_languages, str):
        raw_languages = [raw_languages]
    if not isinstance(raw_languages, list):
        raise ValueError("default_languages must be a string or an array of strings")

    normalized = []
    seen = set()
    for language in raw_languages:
        if not isinstance(language, str):
            raise ValueError("Language entries must be strings")
        language_key = language.strip().lower()
        if language_key not in LANGUAGE_CONFIGS:
            supported = ", ".join(sorted(LANGUAGE_CONFIGS.keys()))
            raise ValueError(
                f"Unsupported language '{language}'. Supported values: {supported}"
            )
        if language_key not in seen:
            normalized.append(language_key)
            seen.add(language_key)

    if not normalized:
        raise ValueError("At least one default language must be configured")
    return normalized


def get_problem_text(data, description_language):
    if description_language == "en":
        title = data.get("title") or data.get("translatedTitle")
        content = data.get("content") or data.get("translatedContent")
        return title, content

    title = data.get("translatedTitle") or data.get("title")
    content = data.get("translatedContent") or data.get("content")
    return title, content


def get_problem(slug, region="cn"):
    url = "https://leetcode.cn/graphql" if region == "cn" else "https://leetcode.com/graphql"
    query = """
    query questionData($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        questionFrontendId
        title
        translatedTitle
        content
        translatedContent
        codeSnippets {
          lang
          langSlug
          code
        }
      }
    }
    """
    payload = {"query": query, "variables": {"titleSlug": slug}}
    headers = {
        "Content-Type": "application/json",
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    result = response.json()
    if "errors" in result:
        raise Exception(f"GraphQL Errors: {result['errors']}")
    question = result.get("data", {}).get("question")
    if not question:
        raise Exception(f"Problem not found: {slug}")
    return question


def get_daily_slug(region="cn"):
    url = "https://leetcode.cn/graphql" if region == "cn" else "https://leetcode.com/graphql"
    query = """
    query questionOfToday {
      todayRecord {
        date
        question {
          titleSlug
        }
      }
    }
    """
    headers = {
        "Content-Type": "application/json",
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
    }
    response = requests.post(url, json={"query": query}, headers=headers)
    response.raise_for_status()
    result = response.json()
    if "errors" in result:
        raise Exception(f"GraphQL Errors: {result['errors']}")
    records = result.get("data", {}).get("todayRecord")
    if not records or not records[0]:
        raise Exception("Daily challenge not found")
    slug = records[0].get("question", {}).get("titleSlug")
    date = records[0].get("date", "unknown")
    if not slug:
        raise Exception("Daily challenge slug not found")
    print(f"Daily challenge ({date}): {slug}")
    return slug


def parse_slug(raw_value):
    slug = raw_value
    if "/" in slug:
        parts = [part for part in slug.split("/") if part]
        if "problems" in parts:
            slug = parts[parts.index("problems") + 1]
    return slug


def parse_code(snippets, snippet_slugs):
    for snippet_slug in snippet_slugs:
        for snippet in snippets:
            if snippet["langSlug"] == snippet_slug:
                return snippet["code"]
    return None


def ensure_parent(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)


def write_text(path, content):
    ensure_parent(path)
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)


def append_line_if_missing(path, line):
    with open(path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    if f"{line}\n" in lines:
        return False

    with open(path, "a", encoding="utf-8") as file:
        if lines and not lines[-1].endswith("\n"):
            file.write("\n")
        file.write(f"{line}\n")
    return True


def build_problem_paths(fs_slug, description_slug, language_key):
    config = LANGUAGE_CONFIGS[language_key]
    md_path = os.path.join(DESCRIPTION_DIR, f"{description_slug}.md")
    code_path = os.path.join(config["problem_dir"], f"{fs_slug}{config['code_ext']}")
    return md_path, code_path


def build_test_path(fs_slug, language_key):
    config = LANGUAGE_CONFIGS[language_key]
    if "test_ext" not in config:
        return None

    base_path = os.path.join(config["test_dir"], fs_slug)
    return f"{base_path}{config['test_ext']}"


def build_problem_md(title, content):
    return f"# {title}\n\n{content}\n"


def build_rust_template(rust_code, md_hint_path):
    has_list_node = "ListNode" in rust_code
    has_tree_node = "TreeNode" in rust_code

    helpers = '\n    // Helper: parse string to type\n    // let nums: Vec<i32> = serde_json::from_str(nums_str).unwrap();'
    if has_list_node:
        helpers += "\n    // Helper: ListNode::from_vec(vec![...]) is useful here if you add it."
    if has_tree_node:
        helpers += "\n    // Helper: TreeNode::from_vec(vec![...]) is useful here."
    helpers += "\n    // This comment should be removed after creation."

    params = []
    match = re.search(r"pub fn (\w+)\s*\((.*?)\)\s*(?:->\s*.*?)?\s*\{", rust_code)
    fn_name = "fn_name"
    if match:
        fn_name = match.group(1)
        params_str = match.group(2)
        for part in params_str.split(","):
            part = part.strip()
            if ":" not in part:
                continue
            name = part.split(":")[0].strip()
            if name.startswith("&"):
                name = name[1:].strip()
            if name.startswith("mut"):
                name = name[3:].strip()
            if name:
                params.append(name)

    silence_args = f"let _ = ({', '.join(['&' + param for param in params])},);" if params else ""
    match_fn = re.search(r"(pub fn \w+\s*\(.*?\)\s*(?:->\s*.*?)?\s*\{)", rust_code, re.DOTALL)
    if match_fn:
        fn_header = match_fn.group(1)
        new_header = fn_header + f'\n        {silence_args}\n        todo!("编写你的逻辑")'
        rust_code = rust_code.replace(fn_header, new_header, 1)

    final_rs_code = f"#![allow(dead_code)]\n\n{rust_code}"
    return f"""{final_rs_code}

// << ---------------- Code below here is only for local use ---------------- >>

pub struct Solution;

// Problem statement file
// "{md_hint_path}"

#[cfg(test)]
mod tests {{
    use super::*;
    use pretty_assertions::assert_eq;
    use rstest::rstest;
{helpers}

    #[rstest]
    #[case("input_str", "expected_str")]
    fn case(#[case] input_str: &str, #[case] expected_str: &str) {{
        // let input: Type = serde_json::from_str(input_str).unwrap();
        // let expected: Type = serde_json::from_str(expected_str).unwrap();
        // let actual = Solution::{fn_name}(input);
        // assert_eq!(actual, expected);
        todo!("Add your test cases here from the MD file using string parsing")
    }}
}}
"""


def build_python_template(code, md_hint_path):
    python_code = code.rstrip() + "\n"
    match = re.search(r"^([ \t]*)def\s+\w+\s*\(.*\)\s*(?:->\s*[^:]+)?:\s*$", python_code, re.MULTILINE)
    if match:
        indent = match.group(1)
        header = match.group(0)
        replacement = f"{header}\n{indent}    pass"
        python_code = python_code.replace(header, replacement, 1)

    return f'''{python_code}

# Problem statement file
# "{md_hint_path}"

import pytest


@pytest.mark.parametrize(
    ("input_data", "expected"),
    [
        # (..., ...),
    ],
)
def test_examples(input_data, expected):
    # actual = Solution().method_name(...)
    # assert actual == expected
    raise NotImplementedError("Fill in pytest examples from the problem statement")
'''


def build_cpp_template(code, title, md_hint_path):
    return f"""// {title}
// Build locally if needed:
// g++ -std=c++20 -O2 -Wall problems/<file>.cpp && ./a.out
// Problem statement file
// "{md_hint_path}"

#include <cassert>
#include <iostream>
#include <vector>

{code}

int main() {{
    // Example:
    // Solution s;
    // std::vector<int> nums{{1, 2, 1, 1, 3}};
    // assert(s.minimumDistance(nums) == 6);
    std::cout << "Fill in examples from the problem statement.\\n";
    return 0;
}}
"""


def build_c_template(code, title, md_hint_path):
    return f"""// {title}
// Build locally if needed:
// gcc -std=c11 -O2 -Wall problems/<file>.c && ./a.out
// Problem statement file
// "{md_hint_path}"

#include <assert.h>
#include <stdio.h>

{code}

int main(void) {{
    // Fill in examples from the problem statement.
    // Example:
    // int nums[] = {{1, 2, 1, 1, 3}};
    // assert(minimumDistance(nums, 5) == 6);
    printf("Fill in examples from the problem statement.\\n");
    return 0;
}}
"""


def build_go_template(code, md_hint_path):
    go_code = code
    if not re.search(r"^\s*package\s+\w+", go_code, re.MULTILINE):
        go_code = f"package problems\n\n{go_code}"

    # Ensure generated function body compiles before user starts solving.
    match_fn = re.search(r"(func\s+\w+\s*\(.*?\)\s*(?:\([^)]*\)|\S+)?\s*\{)", go_code, re.DOTALL)
    if match_fn:
        header = match_fn.group(1)
        go_code = go_code.replace(header, f'{header}\n    panic("todo")', 1)

    go_code_body = re.sub(r"^\s*package\s+\w+\s*\n", "", go_code, count=1, flags=re.MULTILINE).lstrip()

    return f"""package problems

import "testing"

{go_code_body}

// Problem statement file
// "{md_hint_path}"

func Test_example_1(t *testing.T) {{
    // got := minimumDistance(...)
    // want := ...
    // if got != want {{
    //     t.Fatalf("got %v, want %v", got, want)
    // }}
    t.Skip("Fill in go test examples from the problem statement")
}}
"""


def build_typescript_template(code, md_hint_path, fs_slug):
    return f"""import {{ describe, expect, it }} from "vitest";

{code}

// Problem statement file
// "{md_hint_path}"

describe("{fs_slug}", () => {{
    it("example 1", () => {{
        // const actual = minimumDistance([...]);
        // expect(actual).toEqual(...);
        expect.unreachable("Fill in vitest examples from the problem statement");
    }});
}});

export {{}};
"""


def build_test_template(language_key, fs_slug, code):
    return None


def build_code_template(language_key, code, title, md_hint_path, fs_slug):
    if language_key == "rust":
        return build_rust_template(code, md_hint_path)
    if language_key == "python":
        return build_python_template(code, md_hint_path)
    if language_key == "cpp":
        return build_cpp_template(code, title, md_hint_path)
    if language_key == "c":
        return build_c_template(code, title, md_hint_path)
    if language_key == "go":
        return build_go_template(code, md_hint_path)
    if language_key == "typescript":
        return build_typescript_template(code, md_hint_path, fs_slug)
    raise ValueError(f"Unsupported language: {language_key}")


def write_problem_files(data, slug, language_key, description_language):
    config = LANGUAGE_CONFIGS[language_key]
    title, content = get_problem_text(data, description_language)
    frontend_id = data.get("questionFrontendId", "0")
    fs_slug = f"p{frontend_id}_{slug.replace('-', '_')}"
    description_slug = f"p{frontend_id}-{slug}"
    md_path, code_path = build_problem_paths(fs_slug, description_slug, language_key)
    test_path = build_test_path(fs_slug, language_key)
    snippet = parse_code(data["codeSnippets"], config["snippet_slugs"])

    if not snippet:
        raise Exception(f"{config['label']} snippet not found for '{slug}'")

    write_text(md_path, build_problem_md(title, content))
    md_hint_path = os.path.join(DESCRIPTION_DIR, f"{description_slug}.md").replace("/", "\\")
    write_text(code_path, build_code_template(language_key, snippet, title, md_hint_path, fs_slug))
    print(f"Created {md_path}")
    print(f"Created {code_path}")

    test_template = build_test_template(language_key, fs_slug, snippet)
    if test_path and test_template:
        write_text(test_path, test_template)
        print(f"Created {test_path}")

    if language_key == "rust":
        lib_path = os.path.join("rust", "src", "lib.rs")
        mod_line = f"mod {fs_slug};"
        if append_line_if_missing(lib_path, mod_line):
            print(f"Registered module in {lib_path}")
        else:
            print(f"Module {fs_slug} already registered in {lib_path}")


def parse_args():
    config, config_path = load_config()
    default_description_language = normalize_description_language(
        config.get("default_description_language")
    )
    default_languages = normalize_languages(config.get("default_languages"))

    parser = argparse.ArgumentParser(description="Fetch LeetCode problems into local language templates.")
    parser.add_argument("slug_or_url", nargs="?", help="LeetCode problem slug or full URL")
    parser.add_argument("--daily", action="store_true", help="Fetch today's daily challenge")
    parser.add_argument(
        "--lang",
        dest="languages",
        action="append",
        choices=sorted(LANGUAGE_CONFIGS.keys()),
        help="Language to generate. Can be passed multiple times. Defaults to config value or rust.",
    )
    parser.add_argument(
        "--all-langs",
        action="store_true",
        help="Generate files for all supported languages.",
    )
    parser.add_argument(
        "--description-lang",
        choices=["zh", "en"],
        default=default_description_language,
        help="Description language to write into descriptions/*.md. Defaults to config value or zh.",
    )
    args = parser.parse_args()

    if args.daily and args.slug_or_url:
        parser.error("Provide either a slug/url or --daily, not both.")
    if not args.daily and not args.slug_or_url:
        parser.error("Provide a slug/url or use --daily.")

    if args.all_langs:
        selected_languages = list(LANGUAGE_CONFIGS.keys())
    elif args.languages:
        selected_languages = args.languages
    else:
        selected_languages = default_languages

    if config_path:
        print(f"Loaded config: {config_path}")

    return args, selected_languages


def main():
    args, selected_languages = parse_args()
    slug = get_daily_slug(region=DEFAULT_REGION) if args.daily else parse_slug(args.slug_or_url)
    data = get_problem(slug, region=DEFAULT_REGION)

    for language_key in selected_languages:
        write_problem_files(data, slug, language_key, args.description_lang)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Error: {error}")
        sys.exit(1)
