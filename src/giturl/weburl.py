from abc import ABC, abstractmethod
from urllib.parse import quote
import re

from giturl.git import GitRepo
from giturl.remoteurl import RemoteUrl
from giturl.types import ForgeType, Ref, RefType


def get_url_generator_type(forge_type: ForgeType) -> UrlGenerator:
    return {
        ForgeType.GitHub: GitHubUrlGenerator,
        ForgeType.BitBucket: BitBucketUrlGenerator,
        ForgeType.GitLab: GitLabUrlGenerator
    }[forge_type]


class UrlGenerator(ABC):
    @staticmethod
    @abstractmethod
    def create(remote_url: RemoteUrl, repo: GitRepo) -> UrlGenerator:
        pass

    @abstractmethod
    def generate_url(self, relative_path: str, line_number: int | None, ref: Ref) -> str:
        pass


class GitHubUrlGenerator(UrlGenerator):
    @staticmethod
    def create(remote_url: RemoteUrl, repo: GitRepo) -> UrlGenerator:
        match = re.search(r"(?P<account_name>.+?)/(?P<repo_name>.+).git", remote_url.path, re.IGNORECASE)
        if match is None:
            raise Exception(f"Invalid GitHub remote URL path '{remote_url.path}'")
        return GitHubUrlGenerator(repo, remote_url, match["account_name"], match["repo_name"])

    def __init__(self, repo: GitRepo, remote_url: RemoteUrl, account_name: str, repo_name: str):
        self.repo = repo
        self.remote_url = remote_url
        self.account_name = account_name
        self.repo_name = repo_name

    def generate_url(self, relative_path: str, line_number: int | None, ref: Ref) -> str:
        is_path_dir = self.repo.is_dir(relative_path)
        tree_or_blob = "tree" if is_path_dir else "blob"
        refval = quote(ref.value)
        path = quote(relative_path)
        anchor = f"#L{line_number}" if line_number else ""
        return f"https://{self.remote_url.host}/{self.account_name}/{self.repo_name}/{tree_or_blob}/{refval}/{path}{anchor}"


class BitBucketUrlGenerator(UrlGenerator):
    @staticmethod
    def create(remote_url: RemoteUrl, repo: GitRepo) -> UrlGenerator:
        match = re.search(r"(?P<account_name>.+?)/(?P<repo_name>.+).git", remote_url.path, re.IGNORECASE)
        if match is None:
            raise Exception(f"Invalid BitBucket remote URL path '{remote_url.path}'")
        return BitBucketUrlGenerator(repo, remote_url, match["account_name"], match["repo_name"])
    
    def __init__(self, repo: GitRepo, remote_url: RemoteUrl, account_name: str, repo_name: str):
        self.repo = repo
        self.remote_url = remote_url
        self.account_name = account_name
        self.repo_name = repo_name

    def generate_url(self, relative_path: str, line_number: int | None, ref: Ref) -> str:
        refval = quote(ref.value)
        path = quote(relative_path)
        anchor = f"#lines-{line_number}" if line_number else ""
        return f"https://{self.remote_url.host}/{self.account_name}/{self.repo_name}/src/{refval}/{path}{anchor}"


class GitLabUrlGenerator(UrlGenerator):
    @staticmethod
    def create(remote_url: RemoteUrl, repo: GitRepo) -> UrlGenerator:
        match = re.search(r"(?P<org_name>.+?)/(?P<repo_path>.+).git", remote_url.path, re.IGNORECASE)
        if match is None:
            raise Exception(f"Invalid GitLab remote URL path '{remote_url.path}'")
        return GitLabUrlGenerator(repo, remote_url, match["org_name"], match["repo_path"])
    
    def __init__(self, repo: GitRepo, remote_url: RemoteUrl, org_name: str, repo_path: str):
        self.repo = repo
        self.remote_url = remote_url
        self.org_name = org_name
        self.repo_path = repo_path

    def generate_url(self, relative_path: str, line_number: int | None, ref: Ref) -> str:
        is_path_dir = self.repo.is_dir(relative_path)
        tree_or_blob = "tree" if is_path_dir else "blob"
        refval = quote(ref.value)
        path = quote(relative_path)
        qs = "?ref_type=heads" if ref.type == RefType.Branch else ""
        anchor = f"#L{line_number}" if line_number else ""
        return f"https://{self.remote_url.host}/{self.org_name}/{self.repo_path}/-/{tree_or_blob}/{refval}/{path}{qs}{anchor}"
