#!/usr/bin/env python3
"""Install farming infrastructure: hooks, .claude/agents/, settings.json permissions."""

import json
import shutil
import stat
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
HOOKS_SRC = SKILL_DIR / "references" / "hooks"

HOOK_FILES = ["auto-commit.sh", "session-sync.sh", "subagent-push.sh"]

BASE_PERMISSIONS = [
    "Bash(git add:*)",
    "Bash(git commit:*)",
    "Bash(git push:*)",
    "Bash(git pull:*)",
    "Bash(git status:*)",
    "Bash(git diff:*)",
    "Bash(git log:*)",
    "Bash(git rev-parse:*)",
    "Bash(grep:*)",
]

HOOK_CONFIG = {
    "PostToolUse": [
        {
            "matcher": "Write|Edit",
            "hooks": [
                {
                    "type": "command",
                    "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/auto-commit.sh",
                    "timeout": 30,
                }
            ],
        }
    ],
    "SessionStart": [
        {
            "matcher": "",
            "hooks": [
                {
                    "type": "command",
                    "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/session-sync.sh",
                    "timeout": 30,
                }
            ],
        }
    ],
    "SubagentStop": [
        {
            "matcher": ".*-farmer",
            "hooks": [
                {
                    "type": "command",
                    "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/subagent-push.sh",
                    "timeout": 30,
                }
            ],
        }
    ],
}


def install_hooks(repo_root: Path):
    hooks_dst = repo_root / ".claude" / "hooks"
    hooks_dst.mkdir(parents=True, exist_ok=True)

    for name in HOOK_FILES:
        src = HOOKS_SRC / name
        dst = hooks_dst / name
        shutil.copy2(src, dst)
        dst.chmod(dst.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"✓ Installed hooks: {', '.join(HOOK_FILES)}")


def merge_settings(repo_root: Path):
    settings_path = repo_root / ".claude" / "settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    if settings_path.exists():
        settings = json.loads(settings_path.read_text())
    else:
        settings = {}

    # Merge permissions
    perms = settings.setdefault("permissions", {})
    allow = perms.setdefault("allow", [])
    added_perms = [p for p in BASE_PERMISSIONS if p not in allow]
    allow.extend(added_perms)

    # Merge hooks — dedupe by command string
    hooks = settings.setdefault("hooks", {})
    for event, entries in HOOK_CONFIG.items():
        existing = hooks.setdefault(event, [])
        existing_commands = {
            h.get("command")
            for entry in existing
            for h in entry.get("hooks", [])
        }
        for entry in entries:
            new_commands = {h.get("command") for h in entry.get("hooks", [])}
            if not (new_commands & existing_commands):
                existing.append(entry)

    settings_path.write_text(json.dumps(settings, indent=2) + "\n")
    if added_perms:
        print(f"✓ Added permissions: {len(added_perms)}")
    print("✓ Wired hooks into .claude/settings.json")


def ensure_agents_dir(repo_root: Path):
    agents = repo_root / ".claude" / "agents"
    agents.mkdir(parents=True, exist_ok=True)
    print("✓ .claude/agents/ ready")


def main(path: str = "."):
    repo_root = Path(path).resolve()
    if not (repo_root / ".git").exists():
        print("✗ Not a git repo. Run init_vault.py first.")
        sys.exit(1)

    install_hooks(repo_root)
    merge_settings(repo_root)
    ensure_agents_dir(repo_root)

    print("\n✓ Farming infrastructure installed.")
    print("  Next: Claude will interview you to build your first farmer subagent.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Install wiki farming infrastructure")
    parser.add_argument("path", nargs="?", default=".")
    args = parser.parse_args()
    main(args.path)
