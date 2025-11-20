#!/usr/bin/env python3
"""
Create a git tag pointing at the current branch HEAD and update plugin/util.py
'version' value.

Usage:
  ./tools/tag_release.py 1.2.3
  ./tools/tag_release.py 1.2.3 --push --annotated

This script will:
- update the existing 'version' in plugin/util.py (tries assignment or dict key)
- commit that change (unless no change)
- create a git tag (annotated or lightweight)
- optionally push HEAD and the tag
"""
import argparse
import re
import subprocess
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
UTIL_PATH = ROOT / "plugin" / "util.py"


def run(cmd, **kwargs):
    return subprocess.run(cmd, cwd=ROOT, check=True, text=True, **kwargs)


def git_is_clean() -> bool:
    res = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, text=True, capture_output=True)
    return res.stdout.strip() == ""


def update_util_version(new_version: str) -> bool:
    """Return True if file changed, False if not. Raise on failure to find/version replace."""
    txt = UTIL_PATH.read_text(encoding="utf-8")

    # Pattern 1: variable assignment: version = '1.2.3' or version = "1.2.3"
    assign_re = re.compile(r"(^\s*version\s*=\s*)(['\"])([^'\"]+)(['\"])", flags=re.M)
    m = assign_re.search(txt)
    if m:
        current = m.group(3)
        if current == new_version:
            print(f"util.version already {new_version}")
            return False
        def _assign_repl(match):
            return f"{match.group(1)}{match.group(2)}{new_version}{match.group(4)}"
        new_txt = assign_re.sub(_assign_repl, txt, count=1)
        UTIL_PATH.write_text(new_txt, encoding="utf-8")
        print(f"updated {UTIL_PATH} version {current} -> {new_version}")
        return True

    # Pattern 2: dict key: 'version': '1.2.3' or "version": "1.2.3"
    dict_re = re.compile(r"(['\"]version['\"]\s*:\s*)(['\"])([^'\"]+)(['\"])" )
    m2 = dict_re.search(txt)
    if m2:
        current = m2.group(3)
        if current == new_version:
            print(f"util.version already {new_version}")
            return False
        def _dict_repl(match):
            return f"{match.group(1)}{match.group(2)}{new_version}{match.group(4)}"
        new_txt = dict_re.sub(_dict_repl, txt, count=1)
        UTIL_PATH.write_text(new_txt, encoding="utf-8")
        print(f"updated {UTIL_PATH} version {current} -> {new_version}")
        return True

    # Not found: fail explicitly so user can inspect file
    print(f"failed to locate a 'version' entry in {UTIL_PATH}; please update manually", file=sys.stderr)
    raise SystemExit(2)


def main():
    p = argparse.ArgumentParser(description="Update util.version and create a git tag")
    p.add_argument("version", help="Version string to set and tag (e.g. 1.2.3)")
    p.add_argument("--annotated", action="store_true", help="Create an annotated tag")
    p.add_argument("--push", action="store_true", help="Push tag to origin after creating it")
    p.add_argument("--allow-dirty", action="store_true", help="Allow dirty working tree")
    p.add_argument("--tag-name", default=None, help="Tag name to use (defaults to the version string)")
    args = p.parse_args()

    tag_name = args.tag_name or args.version

    if not args.allow_dirty and not git_is_clean():
        print("working tree is not clean; commit or use --allow-dirty", file=sys.stderr)
        sys.exit(1)

    changed = False
    try:
        changed = update_util_version(args.version)
    except SystemExit:
        raise
    except Exception as e:
        print("failed to update util.py:", e, file=sys.stderr)
        sys.exit(1)

    try:
        if changed:
            run(["git", "add", str(UTIL_PATH)])
            run(["git", "commit", "-m", f"Bump version to {args.version}"])
            print("committed util.py change")
        else:
            print("no util.py change to commit")

        # create tag on current HEAD
        if args.annotated:
            run(["git", "tag", "-a", tag_name, "-m", f"Release {tag_name}"])
        else:
            run(["git", "tag", tag_name])
        print("created tag", tag_name)

        if args.push:
            run(["git", "push", "origin", "HEAD"])
            run(["git", "push", "origin", tag_name])
            print("pushed HEAD and tag to origin")

    except subprocess.CalledProcessError as e:
        print("git command failed:", e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
