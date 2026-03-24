import os
import re
from urllib.parse import quote

from giturl import git
from giturl.url_templates import parse_template


class GitUrlError(Exception):
    """Exception raised for errors specific to giturl operations."""
    pass


def get_git_url(path: str, line_number: int | None, branch_mode: bool) -> str:
    abs_path = os.path.abspath(path)
    
    if not os.path.isfile(abs_path) and not os.path.isdir(abs_path):
        raise GitUrlError(f"Path is not an existing file or directory.")

    if line_number is not None and os.path.isdir(abs_path):
        raise GitUrlError("Line number is invalid when path is a directory.")
    
    repo_root = git.get_repo_root(abs_path)
    if repo_root is None:
        raise GitUrlError(f"Path is not part of a git repo.")

    local_branch = git.get_current_branch_name(repo_root)

    remote = get_remote(repo_root, local_branch)
    
    remote_url = git.get_remote_url(repo_root, remote)

    if branch_mode:
        ref = get_branch(repo_root, local_branch)
    else:
        ref = get_short_hash(repo_root)

    path = get_repo_path(repo_root, abs_path)

    url = generate_url(remote_url, {
        "ref": ref,
        "path": path,
        "line_number": str(line_number) if line_number is not None else None,
    })
    
    return url


def get_ref(repo_root: str, branch_mode: bool, local_branch: str | None):
    return get_branch(repo_root, local_branch) if branch_mode else get_short_hash(repo_root)


def get_remote(repo_root: str, local_branch: str | None) -> str:
    if local_branch is not None and (remote := git.get_upstream_remote(repo_root, local_branch)) is not None:
        return remote
        
    remotes = git.get_remotes(repo_root)
    if len(remotes) == 0:
        raise GitUrlError("No git remotes in this repo.")
    elif len(remotes) == 1:
        return remotes[0]
    else:
        raise GitUrlError("Repo has multiple remotes and no upstream to determine the correct one.")


def get_branch(repo_root: str, local_branch: str | None) -> str:
    if local_branch is None:
        raise GitUrlError("Cannot build a branch-based URL with no branch checked out.")
    upstream_branch = git.get_upstream_branch(repo_root, local_branch)
    return upstream_branch or local_branch


def get_short_hash(repo_root: str) -> str:
    if (hash := git.get_short_hash(repo_root)) is None:
        raise GitUrlError("Unable to fetch the latest commit hash. Does the repo have any commits?")
    return hash


def get_repo_path(repo_root, full_path) -> str:
    if os.path.samefile(full_path, repo_root):
        return ""

    rel_path = os.path.relpath(full_path, repo_root).replace(os.sep, "/")
    
    if not git.in_tree(repo_root, rel_path):
        raise GitUrlError(f"Path is not in the git index.")

    return "/" + rel_path


def generate_url(remote_url: str, url_args: dict[str, str | None]) -> str:
    url_configs = {
        r"github.com[:/](?P<account>.+?)/(?P<repo>.+?).git": "https://github.com/{{account}}/{{repo}}/blob/{{ref}}{{path}}{#L{line_number}}",
        r"bitbucket.org[:/](?P<account>.+?)/(?P<repo>.+?).git": "https://bitbucket.org/{{account}}/{{repo}}/src/{{ref}}{{path}}{#line-{line_number}}",
    }

    for pattern, template_str in url_configs.items():
        match = re.search(pattern, remote_url)
        if match:
            template = parse_template(template_str)
            quoted_args = { k: quote(v) for (k, v) in (match.groupdict() | url_args).items() if v is not None }
            return template.apply(quoted_args)
    
    raise GitUrlError(f"No config matched remote URL {remote_url}")
