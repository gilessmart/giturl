import os
import pathlib

from giturl.git import GitRepo
from giturl.remoteurl import RemoteUrl
from giturl.types import ForgeType, Ref, RefType, UsageError
from giturl.weburlgen import create_url_generator


def get_git_url(forge_config: dict[str, ForgeType], path: pathlib.Path, line_number: int | None, ref_type: RefType) -> str:
    if not os.path.isfile(path) and not os.path.isdir(path):
        raise UsageError("path is not an existing file or directory")

    if line_number is not None and os.path.isdir(path):
        raise UsageError("line number is invalid when the path is a directory")
    
    repo = GitRepo.from_path(path)
    if repo is None:
        raise UsageError("path is not part of a git repo")
        
    if not repo.in_tree(path):
        raise UsageError(f"path {path} is not in the git index")

    relative_path = get_relative_path(repo, path)
    ref = get_ref(repo, ref_type)

    remote_url = get_remote_url(repo)
    forge_type = forge_config.get(remote_url.host)
    if forge_type is None:
        raise UsageError(f"remote URL host {remote_url.host} is not configured")
    
    url_generator = create_url_generator(forge_type, repo, remote_url)
    return url_generator.generate_url(relative_path, line_number, ref)


def get_remote_url(repo: GitRepo) -> RemoteUrl:
    local_branch_name = repo.get_current_branch_name()
    # if there's a local branch checked out and it's tracking a remote branch, we'll use that remote branch
    if local_branch_name is not None:
        remote = repo.get_upstream_remote(local_branch_name)
        if remote is not None:
            url = repo.get_remote_url(remote)
            try:
                return RemoteUrl.parse(url)
            except ValueError as e:
                raise UsageError(f"remote URL {url} is unsupported") from e
    
    # else if there's exactly 1 remote branch, we'll default to that
    remotes = repo.get_remotes()
    if len(remotes) == 1:
        url = repo.get_remote_url(remotes[0])
        try:
            return RemoteUrl.parse(url)
        except ValueError as e:
            raise UsageError(f"remote URL {url} is unsupported") from e
    # otherwise we have to error out
    elif len(remotes) == 0:
        raise UsageError("cannot generate URL for repo with no remotes")
    else: # len(remotes) > 1
        raise UsageError("cannot generate URL for repo with multiple remotes but no upstream")


def get_relative_path(repo: GitRepo, path: pathlib.Path) -> str:
    if os.path.samefile(path, repo.root_path):
        return ""
    return os.path.relpath(path, repo.root_path).replace(os.sep, "/")


def get_ref(repo: GitRepo, ref_type: RefType) -> Ref:
    match ref_type:
        case RefType.Branch:
            local_branch_name = repo.get_current_branch_name()
            if local_branch_name == None:
                raise UsageError("cannot build a branch-based URL with no branch checked out")
            branch_name = repo.get_upstream_branch(local_branch_name) or local_branch_name
            return Ref(RefType.Branch, branch_name)
        case RefType.ShortHash:
            hash = repo.get_short_hash()
            # I don't know how we can get here without being able to get a hash, so suppress the error
            return Ref(RefType.ShortHash, hash) # type: ignore
