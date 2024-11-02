"""
UV sync hook

Should run as post-merge, post-checkout or post-rewrite hook
Detect dependency changes from previous commit and run uv sync if necessary
"""

import os
import subprocess
import sys

GIT_DIFF_CMD = ["git", "diff", "--quiet"]
UV_FILES = ["pyproject.toml", "uv.lock", "uv.toml"]

def git_diff(from_ref: str, to_ref: str) -> subprocess.CompletedProcess:
    """
    Run git diff --quiet from_ref to_ref -- pyproject.toml uv.lock uv.toml
    Return code 0 means no changes, 1 means changes
    """
    return subprocess.run([*GIT_DIFF_CMD, from_ref, to_ref, "--", *UV_FILES])
        

def detect_lock_changes() -> bool:
    """
    According to [documentation](https://pre-commit.com/#post-checkout),
    post-checkout hook receives 3 environment variables:
    PRE_COMMIT_FROM_REF, PRE_COMMIT_TO_REF, PRE_COMMIT_CHECKOUT_TYPE
    As obscure as is the third one, we refer to [git documentation](https://git-scm.com/docs/githooks#_post_checkout)
    and know its value is 1 for branch checkout and 0 for file checkout.

    The post-merge hook receives 1 environment variable:
    PRE_COMMIT_IS_SQUASH_MERGE: a flag indicating whether the merge is a squash merge or not.
    We don't care about it, we'll just use it to detect post-merge hook.

    The post-rewrite hook receives 1 environment variable:
    PRE_COMMIT_REWRITE_COMMAND: a flag indicating the rewrite command, it can be rebase or amend.
    """

    # Scenario 1: post-checkout branch
    # only branch checkout is relevant
    # PRE_COMMIT_FROM_REF and PRE_COMMIT_TO_REF differ
    if (from_ref := os.getenv("PRE_COMMIT_FROM_REF")) != (
        to_ref := os.getenv("PRE_COMMIT_TO_REF")
    ):
        return git_diff(from_ref, to_ref).returncode == 1

    # Scenario 2: post-merge
    # Whatever PRE_COMMIT_IS_SQUASH_MERGE is, we need to compare the current HEAD with its parent
    if "PRE_COMMIT_IS_SQUASH_MERGE" in os.environ:
        return git_diff("HEAD^", "HEAD").returncode == 1

    # Scenario 3: post-rewrite
    if os.getenv("PRE_COMMIT_REWRITE_COMMAND") == "rebase":
        return git_diff("ORIG_HEAD", "HEAD").returncode == 1

def main():
    if detect_lock_changes():
        os.execvp("uv", ["uv", "sync", *sys.argv[1:]])


if __name__ == "__main__":
    main()
