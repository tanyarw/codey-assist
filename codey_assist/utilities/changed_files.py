"""This module provides functions for fetching changed files in a Git repository."""

import os
import subprocess
import fnmatch


def get_changed_files_in_dir(directory_path):
    """Fetches the names of changed files within a directory in a Git repository."""

    select_files = []

    cwd = os.getcwd()

    os.chdir(directory_path)
    result = subprocess.run(
        ["git", "diff", "--name-only", directory_path],
        check=True,
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )
    changed_files = result.stdout.splitlines()
    print("Changed files:", changed_files)

    os.chdir(cwd)
    select_files = [
        os.path.join(directory_path, f)
        for f in changed_files
        if f.endswith((".py", ".js", ".md", ".html", ".ts", ".go", ".java"))
    ]

    return select_files


def get_ignore_patterns_dict(root_dir):
    """Reads .gitignore files recursively and returns a dictionary of ignore patterns."""
    ignore_patterns = {}

    for dirpath, _, __ in os.walk(root_dir):
        gitignore_path = os.path.join(dirpath, ".gitignore")
        if os.path.isfile(gitignore_path):
            abs_dir = dirpath
            with open(gitignore_path, "r") as f:
                patterns = [
                    line.strip()
                    for line in f
                    if line.strip()
                    and not line.startswith("#")  # ignore comments and empty lines
                ]
                ignore_patterns[abs_dir] = patterns

    return ignore_patterns


def should_ignore(file_path, ignore_patterns_dict):
    """Checks if a file path should be ignored based on the collected ignore patterns."""

    parent_dir = os.path.dirname(file_path)
    # /Users/tanyawarrier/Desktop/projects/codey-assist/codey_assist/__pycache__/__init__.cpython-311.pyc

    for ignore_dir in ignore_patterns_dict:
        if parent_dir.startswith(ignore_dir):
            dp = parent_dir.replace(ignore_dir, "", 1) + "/"

            for pattern in ignore_patterns_dict[ignore_dir]:
                if fnmatch.fnmatch(os.path.basename(file_path), pattern):
                    return True

                if pattern.endswith("/"):
                    if pattern in dp:
                        return True

                if pattern.endswith("/*"):
                    if pattern[:-1] in dp:
                        return True

    return False
