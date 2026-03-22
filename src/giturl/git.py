import os
import subprocess


def get_repo_root(path: str) -> str | None:
    dir_path = path if os.path.isdir(path) else os.path.dirname(path)
    result = subprocess.run(["git", "rev-parse", "--show-toplevel"], text=True, capture_output=True, encoding="utf-8", cwd=dir_path)
    # normalise the path because git returns a path with forward slashes on Windows
    return os.path.normpath(result.stdout.strip()) if result.returncode == 0 else None # None indicates the path was not part of a git repository


def get_remotes(repo_root: str) -> list[str]:
    remotes = subprocess.check_output(["git", "remote"], text=True, encoding="utf-8", cwd=repo_root).splitlines()
    return [r.strip() for r in remotes if r]


def get_upstream_remote(repo_root: str, local_branch: str) -> str | None:
    result = subprocess.run(
        ["git", "config", "get", f"branch.{local_branch}.remote"],
        text=True,
        capture_output=True,
        encoding="utf-8",
        cwd=repo_root)
    return result.stdout.strip() if result.returncode == 0 else None


def get_upstream_branch(repo_root: str, local_branch: str) -> str | None:
    result = subprocess.run(
        ["git", "config", "get", f"branch.{local_branch}.merge"],
        text=True,
        capture_output=True,
        encoding="utf-8",
        cwd=repo_root)
    return result.stdout.removeprefix("refs/heads/").strip() if result.returncode == 0 else None


def get_remote_url(repo_root: str, remote: str) -> str:
    return subprocess.check_output(["git", "remote", "get-url", remote], text=True, encoding="utf-8", cwd=repo_root).strip()


def get_current_branch_name(repo_root: str) -> str | None:
    branch = subprocess.check_output(["git", "branch", "--show-current"], text=True, encoding="utf-8", cwd=repo_root).strip()
    return branch if branch else None # If the branch name is empty, return None to indicate we're in a detached HEAD state


def get_short_hash(repo_root: str) -> str | None:
    result = subprocess.run(["git", "rev-parse", "--short", "HEAD"], text=True, capture_output=True, cwd=repo_root)
    return result.stdout.strip() if result.returncode == 0 else None # Return None if the command fails, e.g. if there are no commits in the repository


def in_tree(repo_root: str, path: str) -> bool:
    null_terminated_paths = subprocess.check_output(
        ["git", "ls-tree", "-z", "--name-only", "--full-tree", "HEAD", path], 
        text=True,
        encoding="utf-8",
        cwd=repo_root)
    return null_terminated_paths.count("\x00") > 0
