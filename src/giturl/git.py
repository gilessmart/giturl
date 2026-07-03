from dataclasses import dataclass
import os
import pathlib
import re
import subprocess


@dataclass
class RemoteUrl:
    raw: str
    host: str
    path: str

    # The parsing here doesn't get anywhere near supporting all the valid git remote URLs,
    # and it has no support for URL decoding, but hopefully it can manage the github.com, 
    # bitbucket.org and gitlab.com URLs that it's intended for.
    @staticmethod
    def parse(s: str) -> RemoteUrl:
        patterns = [
            r"git@(?P<host>[\w\.]*\w+):(?P<path>.+)",
            r"https://(.+@)?(?P<host>[\w\.]*\w+)(?P<path>.+)"
        ]

        for pattern in patterns:
            match = re.match(pattern, s)
            if match is not None:
                return RemoteUrl(s, match["host"], match["path"].removeprefix("/"))
        
        raise ValueError(f"remote URL {s} did not match any supported pattern")


class GitRepo:
    @staticmethod
    def from_path(path: pathlib.Path) -> GitRepo | None:
        abs_path = os.path.abspath(path)
        dir_path = path if os.path.isdir(abs_path) else os.path.dirname(abs_path)
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
            capture_output=True,
            encoding="utf-8",
            cwd=dir_path)
        
        if result.returncode != 0:
            return None
        
        root_path = os.path.normpath(result.stdout.strip())
        return GitRepo(root_path)

    def __init__(self, root_path: str) -> None:
        self.root_path = root_path

    def in_tree(self, path: pathlib.Path) -> bool:
        result = subprocess.run(
            ["git", "ls-tree", "-z", "--name-only", "--full-tree", "HEAD", os.path.abspath(path)], 
            text=True,
            capture_output=True,
            encoding="utf-8",
            cwd=self.root_path)
        return result.stdout.count("\x00") > 0
    
    def get_current_branch_name(self) -> str | None:
        branch = subprocess.check_output(["git", "branch", "--show-current"], text=True, encoding="utf-8", cwd=self.root_path).strip()
        # If the branch name is empty, return None which indicates we're in a detached HEAD state
        return branch if branch else None

    def get_upstream_remote(self, local_branch: str) -> str | None:
        result = subprocess.run(
            ["git", "config", "get", f"branch.{local_branch}.remote"],
            text=True,
            capture_output=True,
            encoding="utf-8",
            cwd=self.root_path)
        return result.stdout.strip() if result.returncode == 0 else None

    def get_remote_url(self, remote: str) -> str:
        return subprocess.check_output(["git", "remote", "get-url", remote], text=True, encoding="utf-8", cwd=self.root_path).strip()

    def get_remotes(self) -> list[str]:
        remotes = subprocess.check_output(["git", "remote"], text=True, encoding="utf-8", cwd=self.root_path).splitlines()
        return [r.strip() for r in remotes if r]

    def get_upstream_branch(self, local_branch: str) -> str | None:
        result = subprocess.run(
            ["git", "config", "get", f"branch.{local_branch}.merge"],
            text=True,
            capture_output=True,
            encoding="utf-8",
            cwd=self.root_path)
        return result.stdout.removeprefix("refs/heads/").strip() if result.returncode == 0 else None

    def get_short_hash(self) -> str | None:
        result = subprocess.run(["git", "rev-parse", "--short", "HEAD"], text=True, capture_output=True, cwd=self.root_path)
        # Return None if the command fails, e.g. if there are no commits in the repository
        return result.stdout.strip() if result.returncode == 0 else None

    def is_dir(self, relative_path: str) -> bool:
        full_path = os.path.join(self.root_path, relative_path)
        return os.path.isdir(full_path)
