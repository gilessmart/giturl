from typing import Protocol

import pytest

from giturl.git import GitRepo
from giturl.remoteurl import parse_remote_url
from giturl.types import ForgeType, Ref, RefType, UsageError
from giturl.weburlgen import create_url_generator


class IsDirFn(Protocol):
    def __call__(self, relative_path: str) -> bool: ...


def create_mock_repo(*, is_dir: IsDirFn | None = None) -> GitRepo:
    repo = GitRepo("")
    if is_dir is not None:
        repo.is_dir = is_dir
    return repo


@pytest.mark.parametrize("forge_type, remote_url, expected_err_msg", [
    (ForgeType.GitHub, "git@github.com:gilessmart-giturl.git", "invalid GitHub remote URL path 'gilessmart-giturl.git'"),
    (ForgeType.BitBucket, "git@bitbucket.org:gilessmart-giturl.git", "invalid BitBucket remote URL path 'gilessmart-giturl.git'"),
    (ForgeType.GitLab, "git@gitlab.com:gilessmart-giturl.git", "invalid GitLab remote URL path 'gilessmart-giturl.git'")
])
def test__weburlgen__create_url_generator__invalid_remote_url_path(forge_type, remote_url, expected_err_msg):
    repo = create_mock_repo(is_dir = lambda relative_path: False)
    remote_url = parse_remote_url(remote_url)
    with pytest.raises(UsageError) as exinfo:
        create_url_generator(forge_type, repo, remote_url)
    assert str(exinfo.value) == expected_err_msg


@pytest.mark.parametrize("remote_url, relative_path, expected_url", [
    ("git@gitlab.com:gitlab-org/ai/skills.git", ".gitlab-ci.yml", "https://gitlab.com/gitlab-org/ai/skills/-/blob/{ref}/.gitlab-ci.yml"),
    ("git@gitlab.com:gitlab-org/design-strategy/ux-artifacts/motion-service-journey-map.git", ".gitlab-ci.yml", "https://gitlab.com/gitlab-org/design-strategy/ux-artifacts/motion-service-journey-map/-/blob/{ref}/.gitlab-ci.yml")
])
def test__weburlgen__create_url_generator__gitlab_subprojects__file_path(remote_url, relative_path, expected_url):
    repo = create_mock_repo(is_dir = lambda relative_path: False)
    remote_url = parse_remote_url(remote_url)
    generator = create_url_generator(ForgeType.GitLab, repo, remote_url)
    
    ref = Ref(RefType.ShortHash, "abcdef0")
    url = generator.generate_url(relative_path, None, ref)
    assert url == expected_url.format(ref=ref.value)


@pytest.mark.parametrize("forge_type, remote_url, expected_url", [
    (ForgeType.GitHub, "git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/blob/{ref}/README.md"),
    (ForgeType.BitBucket, "git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/{ref}/README.md"),
    (ForgeType.GitLab, "git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/blob/{ref}/README.md")
])
def test__weburlgen__generate_url__ref_type__short_hash(forge_type, remote_url, expected_url):
    repo = create_mock_repo(is_dir = lambda relative_path: False)
    remote_url = parse_remote_url(remote_url)
    generator = create_url_generator(forge_type, repo, remote_url)

    ref = Ref(RefType.ShortHash, "abcdef0")
    url = generator.generate_url("README.md", None, ref)
    assert url == expected_url.format(ref=ref.value)


@pytest.mark.parametrize("forge_type, remote_url, expected_url", [
    (ForgeType.GitHub, "git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/blob/{ref}/README.md"),
    (ForgeType.BitBucket, "git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/{ref}/README.md"),
    (ForgeType.GitLab, "git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/blob/{ref}/README.md?ref_type=heads")
])
def test__weburlgen__generate_url__ref_type__branch(forge_type, remote_url, expected_url):
    repo = create_mock_repo(is_dir = lambda relative_path: False)
    remote_url = parse_remote_url(remote_url)
    generator = create_url_generator(forge_type, repo, remote_url)

    ref = Ref(RefType.Branch, "feature-x")
    url = generator.generate_url("README.md", None, ref)
    assert url == expected_url.format(ref=ref.value)


@pytest.mark.parametrize("forge_type, remote_url, expected_url", [
    (ForgeType.GitHub, "git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/blob/{ref}/README.md#L7"),
    (ForgeType.BitBucket, "git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/{ref}/README.md#lines-7"),
    (ForgeType.GitLab, "git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/blob/{ref}/README.md#L7")
])
def test__weburlgen__generate_url__line_number(forge_type, remote_url, expected_url):
    repo = create_mock_repo(is_dir = lambda relative_path: False)
    remote_url = parse_remote_url(remote_url)
    generator = create_url_generator(forge_type, repo, remote_url)

    ref = Ref(RefType.ShortHash, "abcdef0")
    url = generator.generate_url("README.md", 7, ref)
    assert url == expected_url.format(ref=ref.value)


@pytest.mark.parametrize("forge_type, remote_url, expected_url", [
    (ForgeType.GitHub, "git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/tree/{ref}/"),
    (ForgeType.BitBucket, "git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/{ref}/"),
    (ForgeType.GitLab, "git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/tree/{ref}/")
])
def test__weburlgen__generate_url__root_folder(forge_type, remote_url, expected_url):
    repo = create_mock_repo(is_dir = lambda relative_path: True)
    remote_url = parse_remote_url(remote_url)
    generator = create_url_generator(forge_type, repo, remote_url)

    ref = Ref(RefType.ShortHash, "abcdef0")
    url = generator.generate_url("", None, ref)
    assert url == expected_url.format(ref=ref.value)


@pytest.mark.parametrize("forge_type, remote_url, expected_url", [
    (ForgeType.GitHub, "git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/blob/{ref}/README.md"),
    (ForgeType.BitBucket, "git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/{ref}/README.md"),
    (ForgeType.GitLab, "git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/blob/{ref}/README.md")
])
def test__weburlgen__generate_url__root_level_file(forge_type, remote_url, expected_url):
    repo = create_mock_repo(is_dir = lambda relative_path: False)
    remote_url = parse_remote_url(remote_url)
    generator = create_url_generator(forge_type, repo, remote_url)

    ref = Ref(RefType.ShortHash, "abcdef0")
    url = generator.generate_url("README.md", None, ref)
    assert url == expected_url.format(ref=ref.value)


@pytest.mark.parametrize("forge_type, remote_url, expected_url", [
    (ForgeType.GitHub, "git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/tree/{ref}/a/b"),
    (ForgeType.BitBucket, "git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/{ref}/a/b"),
    (ForgeType.GitLab, "git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/tree/{ref}/a/b")
])
def test__weburlgen__generate_url__nested_folder(forge_type, remote_url, expected_url):
    repo = create_mock_repo(is_dir = lambda relative_path: True)
    remote_url = parse_remote_url(remote_url)
    generator = create_url_generator(forge_type, repo, remote_url)

    ref = Ref(RefType.ShortHash, "abcdef0")
    url = generator.generate_url("a/b", None, ref)
    assert url == expected_url.format(ref=ref.value)


@pytest.mark.parametrize("forge_type, remote_url, expected_url", [
    (ForgeType.GitHub, "git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/blob/{ref}/a/b/foo.txt"),
    (ForgeType.BitBucket, "git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/{ref}/a/b/foo.txt"),
    (ForgeType.GitLab, "git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/blob/{ref}/a/b/foo.txt")
])
def test__weburlgen__generate_url__nested_file(forge_type, remote_url, expected_url):
    repo = create_mock_repo(is_dir = lambda relative_path: False)
    remote_url = parse_remote_url(remote_url)
    generator = create_url_generator(forge_type, repo, remote_url)

    ref = Ref(RefType.ShortHash, "abcdef0")
    url = generator.generate_url("a/b/foo.txt", None, ref)
    assert url == expected_url.format(ref=ref.value)


@pytest.mark.parametrize("forge_type, remote_url, expected_url", [
    (ForgeType.GitHub, "git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/blob/{ref}/file%20-%3D%2B.txt"),
    (ForgeType.BitBucket, "git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/{ref}/file%20-%3D%2B.txt"),
    (ForgeType.GitLab, "git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/blob/{ref}/file%20-%3D%2B.txt")
])
def test__weburlgen__generate_url__path_with_special_chars(forge_type, remote_url, expected_url):
    repo = create_mock_repo(is_dir = lambda relative_path: False)
    remote_url = parse_remote_url(remote_url)
    generator = create_url_generator(forge_type, repo, remote_url)

    ref = Ref(RefType.ShortHash, "abcdef0")
    url = generator.generate_url("file -=+.txt", None, ref)
    assert url == expected_url.format(ref=ref.value)


@pytest.mark.parametrize("forge_type, remote_url, expected_url", [
    (ForgeType.GitHub, "git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/blob/test-branches/_%3D%2B%2C.%40%C2%AC%C2%A3/README.md"),
    (ForgeType.BitBucket, "git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/test-branches/_%3D%2B%2C.%40%C2%AC%C2%A3/README.md"),
    (ForgeType.GitLab, "git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/blob/test-branches/_%3D%2B%2C.%40%C2%AC%C2%A3/README.md?ref_type=heads")
])
def test__weburlgen__generate_url__branch_with_special_chars(forge_type, remote_url, expected_url):
    repo = create_mock_repo(is_dir = lambda relative_path: False)
    remote_url = parse_remote_url(remote_url)
    generator = create_url_generator(forge_type, repo, remote_url)

    ref = Ref(RefType.Branch, "test-branches/_=+,.@¬£")
    url = generator.generate_url("README.md", None, ref)
    assert url == expected_url
