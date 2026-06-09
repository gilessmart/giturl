import os
import re
from urllib.parse import quote

from giturl.git import GitRepo
from giturl.url_templates import parse_template


class GitUrlError(Exception):
    """Exception raised for errors specific to giturl operations."""
    pass


def get_git_url(config: dict[str, str], path: str, line_number: int | None = None, branch_mode: bool = False) -> str:
    if not os.path.isfile(path) and not os.path.isdir(path):
        raise GitUrlError(f"Path is not an existing file or directory.")

    if line_number is not None and os.path.isdir(path):
        raise GitUrlError("Line number is invalid for directory paths.")
    
    repo = GitRepo.from_path(path)
    if repo is None:
        raise GitUrlError("Path is not in a git repo.")
        
    relative_path = get_relative_path(path, repo)

    return generate_url(config, repo, relative_path, line_number, branch_mode)


def get_relative_path(path: str, repo: GitRepo) -> str:
    if os.path.samefile(path, repo.root_path):
        return ""
    
    rel_path = os.path.relpath(path, repo.root_path).replace(os.sep, "/")
    if not repo.in_tree(rel_path):
        raise GitUrlError("Path is not in the git index.")
    
    return "/" + rel_path


def generate_url(config: dict[str, str], repo: GitRepo, relative_path, line_number, branch_mode) -> str:
    local_branch_name = repo.get_current_branch_name()
    remote_url = get_remote_url(repo, local_branch_name)
    ref = get_ref(repo, branch_mode, local_branch_name)
    
    for pattern, template_str in config.items():
        match = re.search(pattern, remote_url)
        if match:
            template = parse_template(template_str)
            args = match.groupdict() | {
                "ref": ref,
                "path": relative_path,
                "line_number": str(line_number) if line_number is not None else None,
            }
            quoted_args = { k: quote(v) for (k, v) in args.items() if v is not None }
            return template.apply(quoted_args)

    raise GitUrlError(f"No config matched remote URL {remote_url}")


def get_remote_url(repo: GitRepo, local_branch_name: str | None) -> str:
    # if there's a local branch checked out and it's tracking a remote branch, we'll use that remote branch
    if local_branch_name is not None:
        remote = repo.get_upstream_remote(local_branch_name)
        if remote is not None:
            return repo.get_remote_url(remote)
    
    # else if there's exactly 1 remote branch, we'll default to that
    remotes = repo.get_remotes()
    if len(remotes) == 1:
        return repo.get_remote_url(remotes[0])
    
    # otherwise we have to error out
    if len(remotes) == 0:
        raise GitUrlError("Repo has no remotes.")
    else: # len(remotes) > 1
        raise GitUrlError("Repo has multiple remotes but no upstream to indicate the correct one.")


def get_ref(repo: GitRepo, branch_mode: bool, local_branch_name: str | None) -> str:
    if branch_mode:
        if local_branch_name == None:
            raise GitUrlError("Cannot build a branch-based URL with no branch checked out")
        return repo.get_upstream_branch(local_branch_name) or local_branch_name
    else:
        hash = repo.get_short_hash()
        if hash is None:
            raise GitUrlError("Unable to fetch the latest commit hash. Does the repo have any commits?")
        return hash
