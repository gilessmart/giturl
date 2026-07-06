from dataclasses import dataclass
import os
import pathlib
import re
import shutil
import subprocess


def ensure_git():
    return shutil.which("git") is not None


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
        """Create a GitRepo from the given file / directory path.

        The given path can identify any file or directory within a repo, 
        regardless of whether it is committed to the index.
        
        Returns:
          A GitRepo instance, or None if `path` was not part of a Git repo.

        Raises:
          FileNotFoundError: The `git` executable was not found.
        """
        abs_path = path.absolute()
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
        """Determine whether the given path is currently in the git tree at HEAD.

        Returns:
          True if the path is part of the git tree at HEAD.
          otherwise False, including if the repo has no commits.
        
        Raises:
          FileNotFoundError: The `git` executable was not found.
        """
        result = subprocess.run(
            ["git", "ls-tree", "-z", "--name-only", "--full-tree", "HEAD", path.absolute()], 
            text=True,
            capture_output=True,
            encoding="utf-8",
            cwd=self.root_path)
        return result.stdout.count("\x00") > 0

    def get_current_branch_name(self) -> str | None:
        """Get the current local branch name.

        Returns:
          The name of the current local branch,
          or None if no branch is checked out i.e. the repo is in detached head state.

        Raises:
          FileNotFoundError: The `git` executable was not found.
        """
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"],
            text=True,
            encoding="utf-8",
            cwd=self.root_path).strip()
        # If the branch name is empty, return None which indicates we're in a detached HEAD state
        return branch if branch else None

    def get_upstream_branch(self, local_branch: str) -> str | None:
        """Get the upstream branch name.
        
        Returns:
          The name of the upstream branch e.g. main,
          or None if the repo doesn't have an upstream branch name in its config.
          
        Raises:
          FileNotFoundError: The `git` executable was not found.
        """
        result = subprocess.run(
            ["git", "config", "get", f"branch.{local_branch}.merge"],
            text=True,
            capture_output=True,
            encoding="utf-8",
            cwd=self.root_path)
        return result.stdout.removeprefix("refs/heads/").strip() if result.returncode == 0 else None

    def get_short_hash(self) -> str | None:
        """Get the short hash of the revision at HEAD.

        Returns:
          The short hash e.g. abcdef0,
          or None if there was no revision at HEAD e.g. if the repo has no commits.
        
        Raises:
          FileNotFoundError: The `git` executable was not found.
        """
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            text=True,
            capture_output=True,
            cwd=self.root_path)
        # Return None if the command fails, e.g. if there are no commits in the repository
        return result.stdout.strip() if result.returncode == 0 else None

    def get_upstream_remote(self, local_branch: str) -> str | None:
        """Get the upstream remote of the given local branch.
        
        Returns:
          The upstream remote name (e.g. origin), 
          or None if the repo doesn't have an upstream remote for the given branch in its config.
        
        Raises:
          FileNotFoundError: The `git` executable was not found.
        """
        result = subprocess.run(
            ["git", "config", "get", f"branch.{local_branch}.remote"],
            text=True,
            capture_output=True,
            encoding="utf-8",
            cwd=self.root_path)
        return result.stdout.strip() if result.returncode == 0 else None

    def get_remote_url(self, remote: str) -> str:
        """Get the URL of the given remote.

        Returns:
          The URL of the given remote e.g. git@github.com:gilessmart/giturl.git.
        
        Raises:
          FileNotFoundError: The `git` executable was not found.
          NameError: The given remote does not exist in the repo.
        """
        return subprocess.check_output(
            ["git", "remote", "get-url", remote],
            text=True,
            encoding="utf-8",
            cwd=self.root_path).strip()

    def get_remotes(self) -> list[str]:
        """List the remotes in the repo.
        
        Returns:
          A list of remote names.
          
        Raises:
          FileNotFoundError: The `git` executable was not found.
        """
        remotes = subprocess.check_output(
            ["git", "remote"],
            text=True,
            encoding="utf-8",
            cwd=self.root_path).splitlines()
        return [r.strip() for r in remotes if r]

    def is_dir(self, relative_path: str) -> bool:
        """Determine whether the given relative path is a directory path.

        Args:
          relative_path: 
            a path relative to the repo root.
        
        Returns:
          True if the given path points to a directory,
          otherwise False (including if the path doesn't exist).
        """
        full_path = os.path.join(self.root_path, relative_path)
        return os.path.isdir(full_path)
