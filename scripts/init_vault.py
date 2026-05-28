#!/usr/bin/env python3
"""Initialize a Karpathy-style wiki: validate privacy, create folders, initial commit."""

import shutil
import subprocess
import sys
from pathlib import Path

GITIGNORE = """\
# macOS
.DS_Store

# Temporary files
*.tmp

# Farmer state (not synced — cloud runs use fallback window)
.farmer-state/
"""


def run(cmd, cwd=None, check=True, capture=False):
    result = subprocess.run(
        cmd, cwd=cwd, check=check,
        capture_output=capture, text=True if capture else None,
    )
    return result


def gh_available():
    return shutil.which("gh") is not None


def repo_is_private(path):
    """Returns True/False/None (if can't determine)."""
    result = run(
        ["gh", "repo", "view", "--json", "visibility", "-q", ".visibility"],
        cwd=path, check=False, capture=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip().upper() == "PRIVATE"


def init_vault(path: Path):
    path = path.resolve()

    # --- gh check ---
    if not gh_available():
        print("✗ gh CLI not found — required to verify repo is private.")
        print("  Install: brew install gh  (macOS) or see https://cli.github.com")
        print("  Then: gh auth login")
        sys.exit(1)

    # --- Privacy check (only if repo has a remote) ---
    has_remote = (path / ".git").exists() and run(
        ["git", "remote", "get-url", "origin"],
        cwd=path, check=False, capture=True,
    ).returncode == 0

    if has_remote:
        private = repo_is_private(path)
        if private is False:
            print("✗ This repository is PUBLIC.")
            print("  Your wiki will contain personal context — it must be private.")
            print("  Fix: gh repo edit --visibility private --accept-visibility-change-consequences")
            sys.exit(1)
        elif private is True:
            print("✓ Repository is private.")
        else:
            print("⚠  Could not verify repo visibility. Make sure it's private before adding personal data.")
    else:
        print("⚠  No git remote configured yet.")
        print("   You can continue locally, but cloud scheduling won't work until you push to a private GitHub repo.")

    # --- Create wiki folders ---
    created = []
    for folder in ["raw", "wiki"]:
        folder_path = path / folder
        if not folder_path.exists():
            folder_path.mkdir(parents=True, exist_ok=True)
            (folder_path / ".gitkeep").touch()
            created.append(folder)
    if created:
        print(f"✓ Created folders: {', '.join(created)}")
    else:
        print("✓ Folders already exist.")

    # --- .gitignore ---
    gitignore = path / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(GITIGNORE)
        print("✓ Created .gitignore")

    # --- Initialize git if needed ---
    if not (path / ".git").exists():
        run(["git", "init"], cwd=path)
        print("✓ Initialized git repository.")

    # --- Commit ---
    run(["git", "add", "-A"], cwd=path)
    result = run(["git", "diff", "--cached", "--quiet"], cwd=path, check=False)
    if result.returncode != 0:
        run(["git", "commit", "-m", "wiki: initialize structure"], cwd=path)
        print("✓ Committed wiki structure.")

        if has_remote:
            push = run(["git", "push"], cwd=path, check=False, capture=True)
            if push.returncode != 0:
                push = run(["git", "push", "-u", "origin", "main"], cwd=path, check=False, capture=True)
            if push.returncode == 0:
                print("✓ Pushed to remote.")
            else:
                print(f"⚠  Push failed: {push.stderr.strip()}")
    else:
        print("✓ Nothing to commit.")

    print(f"\n✓ Wiki scaffolded at {path}")
    print("  Next: Claude will interview you to write your CLAUDE.md schema.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Initialize a Karpathy-style LLM wiki")
    parser.add_argument("path", nargs="?", default=".", help="Wiki path (default: current directory)")
    args = parser.parse_args()
    init_vault(Path(args.path))
