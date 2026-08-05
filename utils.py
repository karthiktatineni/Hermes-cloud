#!/usr/bin/env python3
"""Project utility scripts for common development tasks."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def run_command(cmd: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def git_status(project_root: Path) -> None:
    """Show git status."""
    result = run_command(["git", "status", "--short"], cwd=project_root)
    if result.stdout:
        print(result.stdout)
    else:
        print("Working tree clean")


def git_log(project_root: Path, n: int = 10) -> None:
    """Show recent git log."""
    result = run_command(["git", "log", "--oneline", f"-{n}"], cwd=project_root)
    print(result.stdout or "No commits")


def find_todos(project_root: Path) -> None:
    """Find TODO/FIXME comments in code."""
    for ext in [".py", ".js", ".ts", ".md", ".txt"]:
        for file in project_root.rglob(f"*{ext}"):
            if ".git" in file.parts:
                continue
            try:
                content = file.read_text()
                for i, line in enumerate(content.splitlines(), 1):
                    if "TODO" in line or "FIXME" in line or "HACK" in line:
                        print(f"{file.relative_to(project_root)}:{i}: {line.strip()}")
            except Exception:
                pass


def check_python_syntax(project_root: Path) -> None:
    """Validate Python syntax in all .py files."""
    errors = []
    for file in project_root.rglob("*.py"):
        if ".git" in file.parts or "__pycache__" in file.parts:
            continue
        result = run_command(["python3", "-m", "py_compile", str(file)])
        if result.returncode != 0:
            errors.append(f"{file.relative_to(project_root)}: {result.stderr.strip()}")

    if errors:
        print("Syntax errors found:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print("All Python files syntax OK")


def project_stats(project_root: Path) -> None:
    """Show project statistics."""
    stats = {"files": 0, "lines": 0, "python_files": 0, "python_lines": 0}

    for file in project_root.rglob("*"):
        if file.is_file() and ".git" not in file.parts:
            stats["files"] += 1
            try:
                lines = len(file.read_text().splitlines())
                stats["lines"] += lines
                if file.suffix == ".py":
                    stats["python_files"] += 1
                    stats["python_lines"] += lines
            except Exception:
                pass

    print(json.dumps(stats, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Project utility commands")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="Git status")
    log_parser = subparsers.add_parser("log", help="Git log")
    log_parser.add_argument("-n", type=int, default=10, help="Number of commits")
    subparsers.add_parser("todos", help="Find TODO/FIXME comments")
    subparsers.add_parser("lint", help="Check Python syntax")
    subparsers.add_parser("stats", help="Project statistics")

    args = parser.parse_args()
    project_root = Path(__file__).parent

    commands = {
        "status": git_status,
        "log": lambda p: git_log(p, args.n),
        "todos": find_todos,
        "lint": check_python_syntax,
        "stats": project_stats,
    }

    commands[args.command](project_root)


if __name__ == "__main__":
    main()