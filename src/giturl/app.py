import os

from giturl.git import GitRepo
from giturl.remoteurl import RemoteUrl, parse_remote_url
from giturl.urlgen import Ref, RefType, ProviderType, get_url_generator_type


def get_git_url(config: dict[str, ProviderType], path: str, line_number: int | None = None, branch_mode: bool = False) -> str:
    if not os.path.isfile(path) and not os.path.isdir(path):
        raise Exception("Path is not an existing file or directory.")

    if line_number is not None and os.path.isdir(path):
        raise Exception("Line number is invalid for directory paths.")
    
    repo = GitRepo.from_path(path)
    if repo is None:
        raise Exception("Path is not in a git repo.")
        
    if not repo.in_tree(path):
        raise Exception(f"Path {path} is not in the git index.")

    relative_path = get_relative_path(repo, path)
    ref = get_ref(repo, branch_mode)

    remote_url = get_remote_url(repo)
    provider_type = config.get(remote_url.host)
    if provider_type is None:
        raise Exception("No config matched remote URL")
    
    url_gen_type = get_url_generator_type(provider_type)
    url_generator = url_gen_type.create(remote_url, repo)
    return url_generator.generate_url(relative_path, line_number, ref)


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
        raise Exception("Repo has no remotes.")
    else: # len(remotes) > 1
        raise Exception("Repo has multiple remotes but no upstream to indicate the correct one.")


def get_relative_path(repo: GitRepo, path: str) -> str:
    if os.path.samefile(path, repo.root_path):
        return ""
    return os.path.relpath(path, repo.root_path).replace(os.sep, "/")


def get_ref(repo: GitRepo, branch_mode: bool) -> Ref:
    if branch_mode:
        local_branch_name = repo.get_current_branch_name()
        if local_branch_name == None:
            raise Exception("Cannot build a branch-based URL with no branch checked out")
        branch_name = repo.get_upstream_branch(local_branch_name) or local_branch_name
        return Ref(RefType.Branch, branch_name)
    
    hash = repo.get_short_hash()
    # I don't know how we can get here without being able to get a hash, so suppress the error
    return Ref(RefType.CommitHash, hash) # type: ignore
