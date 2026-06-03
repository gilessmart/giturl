import os
import re
from urllib.parse import quote

from giturl import git
from giturl.url_templates import parse_template


class GitUrlError(Exception):
    """Exception raised for errors specific to giturl operations."""
    pass


def get_git_url(config: dict[str, str], path: str, line_number: int | None = None, branch_mode: bool = False) -> str:
    if not os.path.isfile(path) and not os.path.isdir(path):
        raise GitUrlError(f"Path is not an existing file or directory.")

    if line_number is not None and os.path.isdir(path):
        raise GitUrlError("Line number is invalid for directory paths.")
    
    abs_path = os.path.abspath(path)
    repo_root_path = get_repo_root_path(abs_path)
    local_branch_name = git.get_current_branch_name(repo_root_path)
    remote_url = get_remote_url(repo_root_path, local_branch_name)

    url = generate_url(config, remote_url, {
        "ref": get_branch(repo_root_path, local_branch_name) if branch_mode else get_short_hash(repo_root_path),
        "path": get_repo_path(repo_root_path, abs_path),
        "line_number": str(line_number) if line_number is not None else None,
    })
    
    return url


def get_repo_root_path(abs_path: str) -> str:
    repo_root_path = git.get_repo_root_path(abs_path)
    if repo_root_path is None:
        raise GitUrlError(f"Path is not part of a git repo.")
    return repo_root_path


def get_remote_url(repo_root_path: str, local_branch_name: str | None) -> str:
    remote = get_remote(repo_root_path, local_branch_name)
    return git.get_remote_url(repo_root_path, remote)


def get_remote(repo_root_path: str, local_branch_name: str | None) -> str:
    # if there's a local branch checked out and it's tracking a remote, we'll use that
    if local_branch_name is not None and (remote := git.get_upstream_remote(repo_root_path, local_branch_name)) is not None:
        return remote
        
    remotes = git.get_remotes(repo_root_path)
    if len(remotes) == 0:
        raise GitUrlError("No git remotes in this repo.")
    elif len(remotes) == 1:
        return remotes[0]
    else:
        raise GitUrlError("Repo has multiple remotes but no upstream to indicate the correct one.")


def get_branch(repo_root_path: str, local_branch_name: str | None) -> str:
    if local_branch_name is None:
        raise GitUrlError("Cannot build a branch-based URL with no branch checked out.")
    upstream_branch = git.get_upstream_branch(repo_root_path, local_branch_name)
    # if there's no upstream branch, use the local branch name
    return upstream_branch or local_branch_name


def get_short_hash(repo_root_path: str) -> str:
    if (hash := git.get_short_hash(repo_root_path)) is None:
        raise GitUrlError("Unable to fetch the latest commit hash. Does the repo have any commits?")
    return hash


def get_repo_path(repo_root_path, full_path) -> str:
    if os.path.samefile(full_path, repo_root_path):
        return ""

    rel_path = os.path.relpath(full_path, repo_root_path).replace(os.sep, "/")
    
    if not git.in_tree(repo_root_path, rel_path):
        raise GitUrlError(f"Path is not in the git index.")

    return "/" + rel_path


def generate_url(config: dict[str, str], remote_url: str, url_args: dict[str, str | None]) -> str:
    for pattern, template_str in config.items():
        match = re.search(pattern, remote_url)
        if match:
            template = parse_template(template_str)
            quoted_args = { k: quote(v) for (k, v) in (match.groupdict() | url_args).items() if v is not None }
            return template.apply(quoted_args)
    
    raise GitUrlError(f"No config matched remote URL {remote_url}")
