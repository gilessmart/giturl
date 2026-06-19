import pytest

from giturl.app import get_git_url
from giturl.cli import default_config
import helpers


def test__get_git_url__no_such_file(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    with pytest.raises(Exception) as exinfo:
        get_git_url(default_config, tmp_path / "READYOU.md")
    assert "Path is not an existing file or directory" in str(exinfo.value)


def test__get_git_url__line_number_with_directory_path(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    with pytest.raises(Exception) as exinfo:
        get_git_url(default_config, tmp_path, 20)
    assert "Line number is invalid for directory paths" in str(exinfo.value)


def test__get_git_url__no_repo(tmp_path):
    with pytest.raises(Exception) as exinfo:
        get_git_url(default_config, tmp_path)
    assert "Path is not in a git repo" in str(exinfo.value)


def test__get_git_url__path_not_in_index(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    helpers.write_file(tmp_path / "main.c", "#include <stdio.h>")
    with pytest.raises(Exception) as exinfo:
        get_git_url(default_config, tmp_path / "main.c")
    assert "not in the git index" in str(exinfo.value)


def test__get_git_url__repo_with_no_commits(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    helpers.write_file(tmp_path / "README.md" , "hello\n")
    with pytest.raises(Exception) as exinfo:
        get_git_url(default_config, tmp_path / "README.md")
    assert "not in the git index" in str(exinfo.value)


def test__get_git_url__no_remotes(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    with pytest.raises(Exception) as exinfo:
        get_git_url(default_config, tmp_path / "README.md")
    assert "Repo has no remotes" in str(exinfo.value)


def test__get_git_url__no_upstream_multiple_remotes(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "github", "git@github.com:gilessmart/giturl.git")
    helpers.repo_add_remote(tmp_path, "bitbucket", "git@bitbucket.org:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    with pytest.raises(Exception) as exinfo:
        get_git_url(default_config, tmp_path / "README.md")
    assert "Repo has multiple remotes but no upstream" in str(exinfo.value)


def test__get_git_url__local_remote_url(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    helpers.repo_add_remote(tmp_path, "origin", "file:///Users/giles/repos/giturl")
    with pytest.raises(Exception) as exinfo:
        get_git_url(default_config, tmp_path)
    assert "Remote URL file:///Users/giles/repos/giturl is unsupported" in str(exinfo.value)


def test__get_git_url__no_matching_config(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", "git@github.acme.corp:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    with pytest.raises(Exception) as exinfo:
        get_git_url(default_config, tmp_path / "README.md")
    assert "No config matched remote URL" in str(exinfo.value)


def test__get_git_url__branch_option__detached_head(tmp_path):
    helpers.repo_create(tmp_path, branch="feature-x")
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello 1\n")
    old_hash = helpers.repo_get_current_hash(tmp_path)
    helpers.repo_commit_file(tmp_path, "README.md", "hello 2\n")
    helpers.repo_checkout(tmp_path, old_hash)
    with pytest.raises(Exception) as exinfo:
        get_git_url(default_config, tmp_path / "README.md", branch_mode=True)
    assert "Cannot build a branch-based URL with no branch checked out" in str(exinfo.value)


@pytest.mark.parametrize("remote_url, expected_error_msg", [
    ("git@github.com:gilessmart-giturl.git", "Invalid GitHub remote URL path 'gilessmart-giturl.git'"),
    ("git@bitbucket.org:gilessmart-giturl.git", "Invalid BitBucket remote URL path 'gilessmart-giturl.git'"),
    ("git@gitlab.com:gilessmart-giturl.git", "Invalid GitLab remote URL path 'gilessmart-giturl.git'")
])
def test__get_git_url__invalid_remote_url_paths(tmp_path, remote_url, expected_error_msg):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", remote_url)
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    with pytest.raises(Exception) as exinfo:
        get_git_url(default_config, tmp_path / "README.md")
    assert str(exinfo.value) == expected_error_msg


@pytest.mark.parametrize("remote_url, expected_web_url", [
    ("git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/blob/{hash}/README.md"),
    ("git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/{hash}/README.md"),
    ("git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/blob/{hash}/README.md")
])
def test__get_git_url__single_remote(tmp_path, remote_url, expected_web_url):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", remote_url)
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    url = get_git_url(default_config, tmp_path / "README.md")
    hash = helpers.repo_get_current_hash(tmp_path)
    assert url == expected_web_url.format(hash=hash)


@pytest.mark.parametrize("remote_name, expected_web_url", [
    ("github", "https://github.com/gilessmart/giturl/blob/{hash}/README.md"),
    ("bitbucket", "https://bitbucket.org/gilessmart/giturl/src/{hash}/README.md"),
    ("gitlab", "https://gitlab.com/gilessmart/giturl/-/blob/{hash}/README.md")
])
def test__get_git_url__multiple_remotes_and_upstream(tmp_path, remote_name, expected_web_url):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "github", "git@github.com:gilessmart/giturl.git")
    helpers.repo_add_remote(tmp_path, "bitbucket", "git@bitbucket.org:gilessmart/giturl.git")
    helpers.repo_add_remote(tmp_path, "gitlab", "git@gitlab.com:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    helpers.repo_set_upstream(tmp_path, remote_name)
    url = get_git_url(default_config, tmp_path / "README.md")
    hash = helpers.repo_get_current_hash(tmp_path)
    assert url == expected_web_url.format(hash=hash)


@pytest.mark.parametrize("remote_url, expected_web_url", [
    ("git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/blob/feature-x/README.md"),
    ("git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/feature-x/README.md"),
    ("git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/blob/feature-x/README.md?ref_type=heads")
])
def test__get_git_url__branch_mode(tmp_path, remote_url, expected_web_url):
    helpers.repo_create(tmp_path, branch="feature-x")
    helpers.repo_add_remote(tmp_path, "origin", remote_url)
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    url = get_git_url(default_config, tmp_path / "README.md", branch_mode=True)
    assert url == expected_web_url


@pytest.mark.parametrize("remote_name, expected_web_url", [
    ("github", "https://github.com/gilessmart/giturl/blob/remote_branch/README.md"),
    ("bitbucket", "https://bitbucket.org/gilessmart/giturl/src/remote_branch/README.md"),
    ("gitlab", "https://gitlab.com/gilessmart/giturl/-/blob/remote_branch/README.md?ref_type=heads")
])
def test__get_git_url__branch_mode_with_multiple_remotes_and_upstream(tmp_path, remote_name, expected_web_url):
    helpers.repo_create(tmp_path, "local_branch")
    helpers.repo_add_remote(tmp_path, "github", "git@github.com:gilessmart/giturl.git")
    helpers.repo_add_remote(tmp_path, "bitbucket", "git@bitbucket.org:gilessmart/giturl.git")
    helpers.repo_add_remote(tmp_path, "gitlab", "git@gitlab.com:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    # use a different name for the local and upstream branches
    # so we can tell the upstream branch name is being used
    helpers.repo_set_upstream(tmp_path, remote_name, "remote_branch")
    url = get_git_url(default_config, tmp_path / "README.md", branch_mode=True)
    assert url == expected_web_url


@pytest.mark.parametrize("remote_url, expected_web_url", [
    ("git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/blob/{hash}/README.md#L7"),
    ("git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/{hash}/README.md#lines-7"),
    ("git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/blob/{hash}/README.md#L7")
])
def test__get_git_url__line_num_option(tmp_path, remote_url, expected_web_url):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", remote_url)
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    url = get_git_url(default_config, tmp_path / "README.md", 7)
    hash = helpers.repo_get_current_hash(tmp_path)
    assert url == expected_web_url.format(hash=hash)


@pytest.mark.parametrize("remote_url, expected_web_url", [
    ("git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/tree/{hash}/"),
    ("git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/{hash}/"),
    ("git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/tree/{hash}/")
])
def test__get_git_url__root_level_folder(tmp_path, remote_url, expected_web_url):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", remote_url)
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    url = get_git_url(default_config, tmp_path)
    hash = helpers.repo_get_current_hash(tmp_path)
    assert url == expected_web_url.format(hash=hash)


@pytest.mark.parametrize("remote_url, expected_web_url", [
    ("git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/blob/{hash}/README.md"),
    ("git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/{hash}/README.md"),
    ("git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/blob/{hash}/README.md")
])
def test__get_git_url__root_level_file(tmp_path, remote_url, expected_web_url):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", remote_url)
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    url = get_git_url(default_config, tmp_path / "README.md")
    hash = helpers.repo_get_current_hash(tmp_path)
    assert url == expected_web_url.format(hash=hash)


@pytest.mark.parametrize("remote_url, expected_web_url", [
    ("git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/tree/{hash}/a/b"),
    ("git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/{hash}/a/b"),
    ("git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/tree/{hash}/a/b")
])
def test__get_git_url__nested_folder(tmp_path, remote_url, expected_web_url):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", remote_url)
    helpers.repo_commit_file(tmp_path, "a/b/foo.txt", "hello\n")
    url = get_git_url(default_config, tmp_path / "a/b")
    hash = helpers.repo_get_current_hash(tmp_path)
    assert url == expected_web_url.format(hash=hash)


@pytest.mark.parametrize("remote_url, expected_web_url", [
    ("git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/blob/{hash}/a/b/foo.txt"),
    ("git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/{hash}/a/b/foo.txt"),
    ("git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/blob/{hash}/a/b/foo.txt")
])
def test__get_git_url__nested_file(tmp_path, remote_url, expected_web_url):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", remote_url)
    helpers.repo_commit_file(tmp_path, "a/b/foo.txt", "hello\n")
    url = get_git_url(default_config, tmp_path / "a/b/foo.txt")
    hash = helpers.repo_get_current_hash(tmp_path)
    assert url == expected_web_url.format(hash=hash)


@pytest.mark.parametrize("remote_url, expected_web_url", [
    ("git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/blob/{hash}/file%20-%3D%2B.txt"),
    ("git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/{hash}/file%20-%3D%2B.txt"),
    ("git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/blob/{hash}/file%20-%3D%2B.txt")
])
def test__get_git_url__path_with_special_chars(tmp_path, remote_url, expected_web_url):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", remote_url)
    helpers.repo_commit_file(tmp_path, "file -=+.txt", "hello\n")
    url = get_git_url(default_config, tmp_path / "file -=+.txt")
    hash = helpers.repo_get_current_hash(tmp_path)
    assert url == expected_web_url.format(hash=hash)


@pytest.mark.parametrize("remote_url, expected_web_url", [
    ("git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/blob/test-branches/_%3D%2B%2C.%40%C2%AC%C2%A3/README.md"),
    ("git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/test-branches/_%3D%2B%2C.%40%C2%AC%C2%A3/README.md"),
    ("git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/blob/test-branches/_%3D%2B%2C.%40%C2%AC%C2%A3/README.md?ref_type=heads")
])
def test__get_git_url__local_branch_with_special_chars(tmp_path, remote_url, expected_web_url):
    helpers.repo_create(tmp_path, branch="test-branches/_=+,.@¬£")
    helpers.repo_add_remote(tmp_path, "origin", remote_url)
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    url = get_git_url(default_config, tmp_path / "README.md", branch_mode=True)
    assert url == expected_web_url


@pytest.mark.parametrize("remote_url, expected_web_url", [
    ("git@github.com:gilessmart/giturl.git", "https://github.com/gilessmart/giturl/blob/test-branches/_%3D%2B%2C.%40%C2%AC%C2%A3/README.md"),
    ("git@bitbucket.org:gilessmart/giturl.git", "https://bitbucket.org/gilessmart/giturl/src/test-branches/_%3D%2B%2C.%40%C2%AC%C2%A3/README.md"),
    ("git@gitlab.com:gilessmart/giturl.git", "https://gitlab.com/gilessmart/giturl/-/blob/test-branches/_%3D%2B%2C.%40%C2%AC%C2%A3/README.md?ref_type=heads")
])
def test__get_git_url__upstream_branch_with_special_chars(tmp_path, remote_url, expected_web_url):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", remote_url)
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    helpers.repo_set_upstream(tmp_path, "origin", "test-branches/_=+,.@¬£")
    url = get_git_url(default_config, tmp_path / "README.md", branch_mode=True)
    assert url == expected_web_url
