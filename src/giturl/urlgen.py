from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from urllib.parse import quote
import os
import re

from giturl.errors import GitUrlError
from giturl.git import GitRepo
from giturl.remoteurl import RemoteUrl


class ProviderType(Enum):
    GitHub = auto()
    BitBucket = auto()
    GitLab = auto()


class RefType(Enum):
    Branch = auto()
    CommitHash = auto()


@dataclass
class Ref:
    type: RefType
    value: str


def get_url_generator_type(provider_type: ProviderType) -> UrlGenerator:
    return {
        ProviderType.GitHub: GitHubUrlGenerator,
        ProviderType.BitBucket: BitBucketUrlGenerator,
        ProviderType.GitLab: GitLabUrlGenerator
    }[provider_type]


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
            raise GitUrlError(f"Invalid GitHub remote URL path '{remote_url.path}'")
        return GitHubUrlGenerator(repo, remote_url.host, match["account_name"], match["repo_name"])

    def __init__(self, repo: GitRepo, domain: str, account_name: str, repo_name: str):
        self.repo = repo
        self.domain = domain
        self.account_name = account_name
        self.repo_name = repo_name

    def generate_url(self, relative_path: str, line_number: int | None, ref: Ref) -> str:
        domain = quote(self.domain)
        account_name = quote(self.account_name)
        repo_name = quote(self.repo_name)
        is_path_dir = is_dir(self.repo, relative_path)
        tree_or_blob = "tree" if is_path_dir else "blob"
        refval = quote(ref.value)
        path = quote(relative_path)
        anchor = f"#L{line_number}" if line_number else ""
        return f"https://{domain}/{account_name}/{repo_name}/{tree_or_blob}/{refval}/{path}{anchor}"


class BitBucketUrlGenerator(UrlGenerator):
    @staticmethod
    def create(remote_url: RemoteUrl, repo: GitRepo) -> UrlGenerator:
        match = re.search(r"(?P<account_name>.+?)/(?P<repo_name>.+).git", remote_url.path, re.IGNORECASE)
        if match is None:
            raise GitUrlError(f"Invalid BitBucket remote URL path '{remote_url.path}'")
        return BitBucketUrlGenerator(repo, remote_url.host, match["account_name"], match["repo_name"])
    
    def __init__(self, repo: GitRepo, domain: str, account_name: str, repo_name: str):
        self.repo = repo
        self.domain = domain
        self.account_name = account_name
        self.repo_name = repo_name

    def generate_url(self, relative_path: str, line_number: int | None, ref: Ref) -> str:
        domain = quote(self.domain)
        account_name = quote(self.account_name)
        repo_name = quote(self.repo_name)
        refval = quote(ref.value)
        path = quote(relative_path)
        anchor = f"#lines-{line_number}" if line_number else ""
        return f"https://{domain}/{account_name}/{repo_name}/src/{refval}/{path}{anchor}"


class GitLabUrlGenerator(UrlGenerator):
    @staticmethod
    def create(remote_url: RemoteUrl, repo: GitRepo) -> UrlGenerator:
        match = re.search(r"(?P<org_name>.+?)/(?P<repo_path>.+).git", remote_url.path, re.IGNORECASE)
        if match is None:
            raise GitUrlError(f"Invalid GitLab remote URL path '{remote_url.path}'")
        return GitLabUrlGenerator(repo, remote_url.host, match["org_name"], match["repo_path"])
    
    def __init__(self, repo: GitRepo, domain: str, org_name: str, repo_path: str):
        self.repo = repo
        self.domain = domain
        self.org_name = org_name
        self.repo_path = repo_path

    def generate_url(self, relative_path: str, line_number: int | None, ref: Ref) -> str:
        domain = quote(self.domain)
        org_name = quote(self.org_name)
        repo_path = quote(self.repo_path)
        is_path_dir = is_dir(self.repo, relative_path)
        tree_or_blob = "tree" if is_path_dir else "blob"
        refval = quote(ref.value)
        path = quote(relative_path)
        qs = "?ref_type=heads" if ref.type == RefType.Branch else ""
        anchor = f"#L{line_number}" if line_number else ""
        return f"https://{domain}/{org_name}/{repo_path}/-/{tree_or_blob}/{refval}/{path}{qs}{anchor}"


def is_dir(repo: GitRepo, relative_path: str) -> bool:
    full_path = os.path.join(repo.root_path, relative_path)
    return os.path.isdir(full_path)
