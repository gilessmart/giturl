from enum import Enum, auto
import os

from giturl import urlgen
from giturl.urlgen import Ref, RefType
from giturl.errors import GitUrlError
from giturl.git import GitRepo
from giturl.remoteurl import RemoteUrl, parse_remote_url


class ServiceType(Enum):
    GitHub = auto()
    BitBucket = auto()
    GitLab = auto()


def get_git_url(config: dict[str, ServiceType], path: str, line_number: int | None = None, branch_mode: bool = False) -> str:
    if not os.path.isfile(path) and not os.path.isdir(path):
        raise GitUrlError("Path is not an existing file or directory.")

    if line_number is not None and os.path.isdir(path):
        raise GitUrlError("Line number is invalid for directory paths.")
    
    repo = GitRepo.from_path(path)
    if repo is None:
        raise GitUrlError("Path is not in a git repo.")
        
    if not repo.in_tree(path):
        raise GitUrlError(f"Path {path} is not in the git index.")

    remote_url = get_remote_url(repo)
    generator = get_url_generator(config, repo, remote_url)

    relative_path = get_relative_path(path, repo)
    ref = get_ref(repo, branch_mode)
    return generator.generate_url(relative_path, line_number, ref)


def get_url_generator(config: dict[str, ServiceType], repo: GitRepo, remote_url: RemoteUrl) -> urlgen.UrlGenerator:
    scheme = config.get(remote_url.host)
    if scheme is None:
        raise GitUrlError("No config matched remote URL")
    generator = {
        ServiceType.GitHub: urlgen.GitHubUrlGenerator,
        ServiceType.BitBucket: urlgen.BitBucketUrlGenerator,
        ServiceType.GitLab: urlgen.GitLabUrlGenerator
    }[scheme]
    return generator.create(remote_url, repo)


def get_remote_url(repo: GitRepo) -> RemoteUrl:
    local_branch_name = repo.get_current_branch_name()
    # if there's a local branch checked out and it's tracking a remote branch, we'll use that remote branch
    if local_branch_name is not None:
        remote = repo.get_upstream_remote(local_branch_name)
        if remote is not None:
            url = repo.get_remote_url(remote)
            return parse_remote_url(url)
    
    # else if there's exactly 1 remote branch, we'll default to that
    remotes = repo.get_remotes()
    if len(remotes) == 1:
        url = repo.get_remote_url(remotes[0])
        return parse_remote_url(url)
    # otherwise we have to error out
    elif len(remotes) == 0:
        raise GitUrlError("Repo has no remotes.")
    else: # len(remotes) > 1
        raise GitUrlError("Repo has multiple remotes but no upstream to indicate the correct one.")


def get_relative_path(path: str, repo: GitRepo) -> str:
    if os.path.samefile(path, repo.root_path):
        return ""
    return os.path.relpath(path, repo.root_path).replace(os.sep, "/")


def get_ref(repo: GitRepo, branch_mode: bool) -> Ref:
    if branch_mode:
        local_branch_name = repo.get_current_branch_name()
        if local_branch_name == None:
            raise GitUrlError("Cannot build a branch-based URL with no branch checked out")
        branch_name = repo.get_upstream_branch(local_branch_name) or local_branch_name
        return Ref(RefType.Branch, branch_name)
    
    hash = repo.get_short_hash()
    if hash is None:
        raise GitUrlError("Unable to fetch the latest commit hash. Does the repo have any commits?")
    return Ref(RefType.CommitHash, hash)
