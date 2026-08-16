#!/usr/bin/env python3
"""DevKit Stop hook — gate checks before Claude Code finishes a turn.

Wired from settings.json as a `Stop` hook. Reads the hook payload on stdin and
inspects the current git state. Exit 0 lets the turn end; exit 2 blocks it and
feeds the message on stderr back to Claude so it can fix the problem.

Disabled by default. It only runs when `.agent/completion-check.json` exists and
sets `"enabled": true`, so dropping DevKit's settings.json into a project never
silently starts blocking turns.

Config (`.agent/completion-check.json`), all keys optional:

    {
      "enabled": true,
      "base_ref": "main",
      "checks": {
        "forbidden_paths": true,
        "plan_exists": true,
        "tests_touched": false
      },
      "source_globs": ["**/*.ts", "**/*.tsx", "**/*.py", "**/*.cs"],
      "test_globs": ["**/*.test.*", "**/*.spec.*", "**/test_*.py", "tests/**"],
      "ignore_globs": ["docs/**", "**/*.md"]
    }

Stdlib only. No third-party imports, no network.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

DEFAULT_SOURCE_GLOBS = [
    "**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx", "**/*.mjs", "**/*.cjs",
    "**/*.py", "**/*.cs", "**/*.go", "**/*.rs", "**/*.rb", "**/*.java",
    "**/*.kt", "**/*.php", "**/*.sql", "**/*.vue", "**/*.svelte",
]

DEFAULT_TEST_GLOBS = [
    "**/*.test.*", "**/*.spec.*", "**/test_*.py", "**/*_test.py",
    "**/*Test.cs", "**/*Tests.cs", "**/Tests.*/**", "**/*_test.go",
    "tests/**", "test/**", "__tests__/**", "spec/**",
]

DEFAULT_IGNORE_GLOBS = [
    "**/*.md", "**/*.mdx", "**/*.txt", "docs/**",
    ".agent/**", ".claude/**", "**/generated/**", "**/*.generated.*",
]

DEFAULT_CHECKS = {
    "forbidden_paths": True,
    "plan_exists": True,
    "tests_touched": False,
}


# --------------------------------------------------------------------------
# glob matching
# --------------------------------------------------------------------------

def glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Translate a gitignore-flavored glob into an anchored regex.

    Handles the forms OWNERSHIP.md actually uses: `**/` prefixes, `/**`
    suffixes, `*` (one segment), `?`, and `[...]` character classes.
    """
    pattern = pattern.strip().strip("`").strip("/")
    out: list[str] = []
    i = 0
    n = len(pattern)
    while i < n:
        c = pattern[i]
        if pattern.startswith("**/", i):
            out.append("(?:[^/]+/)*")
            i += 3
        elif pattern.startswith("/**", i) and i + 3 == n:
            out.append("(?:/.*)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif c == "*":
            out.append("[^/]*")
            i += 1
        elif c == "?":
            out.append("[^/]")
            i += 1
        elif c == "[":
            j = pattern.find("]", i + 1)
            if j == -1:
                out.append(re.escape(c))
                i += 1
            else:
                body = pattern[i + 1 : j]
                if body.startswith("!"):
                    body = "^" + body[1:]
                out.append("[" + body + "]")
                i = j + 1
        else:
            out.append(re.escape(c))
            i += 1
    return re.compile("^" + "".join(out) + "$")


def matches_any(path: str, patterns: list[str]) -> str | None:
    """Return the first pattern that matches `path`, or None."""
    for pat in patterns:
        try:
            if glob_to_regex(pat).match(path):
                return pat
        except re.error:
            continue
    return None


# --------------------------------------------------------------------------
# git
# --------------------------------------------------------------------------

def git(root: Path, *args: str) -> str:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return proc.stdout if proc.returncode == 0 else ""


def changed_files(root: Path, base_ref: str) -> list[str]:
    """Files changed on this branch plus anything dirty in the working tree."""
    files: set[str] = set()

    merge_base = git(root, "merge-base", base_ref, "HEAD").strip()
    if merge_base:
        for line in git(root, "diff", "--name-only", merge_base, "HEAD").splitlines():
            if line.strip():
                files.add(line.strip())

    # -uall so untracked files are listed individually rather than collapsed
    # into a bare "?? src/" directory entry.
    for line in git(root, "status", "--porcelain", "-uall").splitlines():
        # "XY path" or "XY old -> new" for renames
        entry = line[3:].strip() if len(line) > 3 else ""
        if not entry:
            continue
        if " -> " in entry:
            entry = entry.split(" -> ", 1)[1]
        files.add(entry.strip().strip('"'))

    return sorted(f for f in files if f)


# --------------------------------------------------------------------------
# OWNERSHIP.md
# --------------------------------------------------------------------------

def forbidden_globs(root: Path) -> list[str]:
    """Parse the `## forbidden` section of .agent/OWNERSHIP.md.

    Reads backticked globs from list items, skipping HTML-comment blocks so the
    template's commented-out suggestions are not treated as live rules.
    """
    path = root / ".agent" / "OWNERSHIP.md"
    if not path.is_file():
        return []

    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []

    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

    globs: list[str] = []
    in_section = False
    for line in text.splitlines():
        heading = re.match(r"^#{1,6}\s+(.*)$", line)
        if heading:
            in_section = heading.group(1).strip().lower().startswith("forbidden")
            continue
        if not in_section:
            continue
        if not line.lstrip().startswith(("-", "*", "+")):
            continue
        item = line.lstrip()[1:]
        # Only the part before the em-dash rationale, and only backticked globs.
        item = re.split(r"\s+—\s+|\s+--\s+", item, maxsplit=1)[0]
        globs.extend(m.strip() for m in re.findall(r"`([^`]+)`", item))

    return [g for g in globs if g]


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------

def check_forbidden_paths(root: Path, files: list[str]) -> list[str]:
    globs = forbidden_globs(root)
    if not globs:
        return []
    hits = []
    for f in files:
        pat = matches_any(f, globs)
        if pat:
            hits.append(f"  {f}  (matches forbidden glob `{pat}`)")
    if not hits:
        return []
    shown, extra = hits[:10], len(hits) - 10
    if extra > 0:
        shown.append(f"  ... and {extra} more")
    return [
        "Forbidden-path edits are present in the diff. The `safe-edit` rule in "
        "CLAUDE.md should have blocked these:",
        *shown,
        "Revert them and load `escalation` to produce a draft patch for a human. "
        "Do not re-apply them yourself.",
    ]


def check_plan_exists(root: Path, source_files: list[str]) -> list[str]:
    if not source_files:
        return []
    tickets = root / ".agent" / "tickets"
    if tickets.is_dir() and any(tickets.glob("*/plan.md")):
        return []
    return [
        "Source files changed but no `.agent/tickets/<ticket-id>/plan.md` exists. "
        "Gate 1 requires a plan before code:",
        *[f"  {f}" for f in source_files[:10]],
        "Load the `think` skill and write plan.md, or move these changes out of "
        "this branch.",
    ]


def check_tests_touched(files: list[str], test_globs: list[str],
                        source_files: list[str]) -> list[str]:
    if not source_files:
        return []
    if any(matches_any(f, test_globs) for f in files):
        return []
    return [
        "Source files changed but no test file was added or modified. "
        "`test-first` requires a failing test before the fix:",
        *[f"  {f}" for f in source_files[:10]],
        "Add the test, or state explicitly why this change has no testable "
        "behavior (pure docs, type-only, comment edits).",
    ]


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    # Never re-block a turn that is already stopping because of this hook.
    if payload.get("stop_hook_active"):
        return 0

    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())

    config_path = root / ".agent" / "completion-check.json"
    if not config_path.is_file():
        return 0
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"completion-check: cannot read {config_path}: {exc}", file=sys.stderr)
        return 0
    if not config.get("enabled"):
        return 0

    if not (root / ".git").exists():
        return 0

    checks = {**DEFAULT_CHECKS, **config.get("checks", {})}
    base_ref = config.get("base_ref", "main")
    source_globs = config.get("source_globs", DEFAULT_SOURCE_GLOBS)
    test_globs = config.get("test_globs", DEFAULT_TEST_GLOBS)
    ignore_globs = config.get("ignore_globs", DEFAULT_IGNORE_GLOBS)

    files = changed_files(root, base_ref)
    if not files:
        return 0

    source_files = [
        f for f in files
        if matches_any(f, source_globs)
        and not matches_any(f, ignore_globs)
        and not matches_any(f, test_globs)
    ]

    problems: list[str] = []
    if checks.get("forbidden_paths"):
        problems += check_forbidden_paths(root, files)
    if checks.get("plan_exists"):
        problems += check_plan_exists(root, source_files)
    if checks.get("tests_touched"):
        problems += check_tests_touched(files, test_globs, source_files)

    if not problems:
        return 0

    print("DevKit completion check failed:", file=sys.stderr)
    for line in problems:
        print(line, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
