import pytest

from giturl.git import GitRepo
from giturl.remoteurl import parse_remote_url
from giturl.types import ForgeType, Ref, RefType
from giturl.weburl import get_url_generator_type


@pytest.mark.parametrize("forge_type, remote_url, expected_err_msg", [
    (ForgeType.GitHub, "git@github.com:gilessmart-giturl.git", "Invalid GitHub remote URL path 'gilessmart-giturl.git'"),
    (ForgeType.BitBucket, "git@bitbucket.org:gilessmart-giturl.git", "Invalid BitBucket remote URL path 'gilessmart-giturl.git'"),
    (ForgeType.GitLab, "git@gitlab.com:gilessmart-giturl.git", "Invalid GitLab remote URL path 'gilessmart-giturl.git'")
])
def test__weburl__create__invalid_remote_url_path(forge_type, remote_url, expected_err_msg):
    repo = GitRepo("")
    repo.is_dir = lambda relative_path: False
    remote_url = parse_remote_url(remote_url)
    generator_type = get_url_generator_type(forge_type)
    with pytest.raises(Exception) as exinfo:
        generator_type.create(remote_url, repo)
    assert str(exinfo.value) == expected_err_msg


@pytest.mark.parametrize("forge_type, remote_url, expected_web_url", [
    (ForgeType.GitHub, "git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/blob/{ref}/README.md"),
    (ForgeType.BitBucket, "git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/{ref}/README.md"),
    (ForgeType.GitLab, "git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/blob/{ref}/README.md")
])
def test__weburl__get_git_url__ref_type__short_hash(forge_type, remote_url, expected_web_url):
    repo = GitRepo("")
    repo.is_dir = lambda relative_path: False
    remote_url = parse_remote_url(remote_url)
    generator = get_url_generator_type(forge_type).create(remote_url, repo)

    ref = Ref(RefType.ShortHash, "abcdef0")
    url = generator.generate_url("README.md", None, ref)
    assert url == expected_web_url.format(ref=ref.value)


@pytest.mark.parametrize("forge_type, remote_url, expected_web_url", [
    (ForgeType.GitHub, "git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/blob/{ref}/README.md"),
    (ForgeType.BitBucket, "git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/{ref}/README.md"),
    (ForgeType.GitLab, "git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/blob/{ref}/README.md?ref_type=heads")
])
def test__weburl__get_git_url__ref_type__branch(forge_type, remote_url, expected_web_url):
    repo = GitRepo("")
    repo.is_dir = lambda relative_path: False
    remote_url = parse_remote_url(remote_url)
    generator = get_url_generator_type(forge_type).create(remote_url, repo)

    ref = Ref(RefType.Branch, "feature-x")
    url = generator.generate_url("README.md", None, ref)
    assert url == expected_web_url.format(ref=ref.value)


@pytest.mark.parametrize("forge_type, remote_url, expected_web_url", [
    (ForgeType.GitHub, "git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/blob/{ref}/README.md#L7"),
    (ForgeType.BitBucket, "git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/{ref}/README.md#lines-7"),
    (ForgeType.GitLab, "git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/blob/{ref}/README.md#L7")
])
def test__weburl__get_git_url__line_number(forge_type, remote_url, expected_web_url):
    repo = GitRepo("")
    repo.is_dir = lambda relative_path: False
    remote_url = parse_remote_url(remote_url)
    generator = get_url_generator_type(forge_type).create(remote_url, repo)

    ref = Ref(RefType.ShortHash, "abcdef0")
    url = generator.generate_url("README.md", 7, ref)
    assert url == expected_web_url.format(ref=ref.value)


@pytest.mark.parametrize("forge_type, remote_url, expected_web_url", [
    (ForgeType.GitHub, "git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/tree/{ref}/"),
    (ForgeType.BitBucket, "git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/{ref}/"),
    (ForgeType.GitLab, "git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/tree/{ref}/")
])
def test__weburl__get_git_url__root_folder(forge_type, remote_url, expected_web_url):
    repo = GitRepo("")
    repo.is_dir = lambda relative_path: True
    remote_url = parse_remote_url(remote_url)
    generator = get_url_generator_type(forge_type).create(remote_url, repo)

    ref = Ref(RefType.ShortHash, "abcdef0")
    url = generator.generate_url("", None, ref)
    assert url == expected_web_url.format(ref=ref.value)


@pytest.mark.parametrize("forge_type, remote_url, expected_web_url", [
    (ForgeType.GitHub, "git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/blob/{ref}/README.md"),
    (ForgeType.BitBucket, "git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/{ref}/README.md"),
    (ForgeType.GitLab, "git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/blob/{ref}/README.md")
])
def test__weburl__get_git_url__root_level_file(forge_type, remote_url, expected_web_url):
    repo = GitRepo("")
    repo.is_dir = lambda relative_path: False
    remote_url = parse_remote_url(remote_url)
    generator = get_url_generator_type(forge_type).create(remote_url, repo)

    ref = Ref(RefType.ShortHash, "abcdef0")
    url = generator.generate_url("README.md", None, ref)
    assert url == expected_web_url.format(ref=ref.value)


@pytest.mark.parametrize("forge_type, remote_url, expected_web_url", [
    (ForgeType.GitHub, "git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/tree/{ref}/a/b"),
    (ForgeType.BitBucket, "git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/{ref}/a/b"),
    (ForgeType.GitLab, "git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/tree/{ref}/a/b")
])
def test__weburl__get_git_url__nested_folder(forge_type, remote_url, expected_web_url):
    repo = GitRepo("")
    repo.is_dir = lambda relative_path: True
    remote_url = parse_remote_url(remote_url)
    generator = get_url_generator_type(forge_type).create(remote_url, repo)

    ref = Ref(RefType.ShortHash, "abcdef0")
    url = generator.generate_url("a/b", None, ref)
    assert url == expected_web_url.format(ref=ref.value)


@pytest.mark.parametrize("forge_type, remote_url, expected_web_url", [
    (ForgeType.GitHub, "git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/blob/{ref}/a/b/foo.txt"),
    (ForgeType.BitBucket, "git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/{ref}/a/b/foo.txt"),
    (ForgeType.GitLab, "git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/blob/{ref}/a/b/foo.txt")
])
def test__weburl__get_git_url__nested_file(forge_type, remote_url, expected_web_url):
    repo = GitRepo("")
    repo.is_dir = lambda relative_path: False
    remote_url = parse_remote_url(remote_url)
    generator = get_url_generator_type(forge_type).create(remote_url, repo)

    ref = Ref(RefType.ShortHash, "abcdef0")
    url = generator.generate_url("a/b/foo.txt", None, ref)
    assert url == expected_web_url.format(ref=ref.value)


@pytest.mark.parametrize("forge_type, remote_url, expected_web_url", [
    (ForgeType.GitHub, "git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/blob/{ref}/file%20-%3D%2B.txt"),
    (ForgeType.BitBucket, "git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/{ref}/file%20-%3D%2B.txt"),
    (ForgeType.GitLab, "git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/blob/{ref}/file%20-%3D%2B.txt")
])
def test__weburl__get_git_url__path_with_special_chars(forge_type, remote_url, expected_web_url):
    repo = GitRepo("")
    repo.is_dir = lambda relative_path: False
    remote_url = parse_remote_url(remote_url)
    generator = get_url_generator_type(forge_type).create(remote_url, repo)

    ref = Ref(RefType.ShortHash, "abcdef0")
    url = generator.generate_url("file -=+.txt", None, ref)
    assert url == expected_web_url.format(ref=ref.value)


@pytest.mark.parametrize("forge_type, remote_url, expected_web_url", [
    (ForgeType.GitHub, "git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/blob/test-branches/_%3D%2B%2C.%40%C2%AC%C2%A3/README.md"),
    (ForgeType.BitBucket, "git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/test-branches/_%3D%2B%2C.%40%C2%AC%C2%A3/README.md"),
    (ForgeType.GitLab, "git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/blob/test-branches/_%3D%2B%2C.%40%C2%AC%C2%A3/README.md?ref_type=heads")
])
def test__weburl__get_git_url__branch_with_special_chars(forge_type, remote_url, expected_web_url):
    repo = GitRepo("")
    repo.is_dir = lambda relative_path: False
    remote_url = parse_remote_url(remote_url)
    generator = get_url_generator_type(forge_type).create(remote_url, repo)

    ref = Ref(RefType.Branch, "test-branches/_=+,.@¬£")
    url = generator.generate_url("README.md", None, ref)
    assert url == expected_web_url
