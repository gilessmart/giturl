import pytest

from giturl.cli import config as defaultConfig
from giturl.core import GitUrlError, get_git_url
import helpers


def test_core__no_such_file(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    helpers.repo_add_remote(tmp_path, "github", "git@github.com:gilessmart/giturl.git")
    with pytest.raises(GitUrlError) as exinfo:
        get_git_url(defaultConfig, tmp_path / "READYOU.md")
    assert "Path is not an existing file or directory" in str(exinfo.value)


def test_core__line_number_with_directory_path(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    helpers.repo_add_remote(tmp_path, "github", "git@github.com:gilessmart/giturl.git")
    with pytest.raises(GitUrlError) as exinfo:
        get_git_url(defaultConfig, tmp_path, 20)
    assert "Line number is invalid for directory paths" in str(exinfo.value)


def test_core__no_repo(tmp_path):
    with pytest.raises(GitUrlError) as exinfo:
        get_git_url(defaultConfig, tmp_path)
    assert "Path is not part of a git repo" in str(exinfo.value)


def test_core__no_remotes(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    with pytest.raises(GitUrlError) as exinfo:
        get_git_url(defaultConfig, tmp_path / "README.md")
    assert "No git remotes" in str(exinfo.value)


def test_core__no_upstream_multiple_remotes(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "github", "git@github.com:gilessmart/giturl.git")
    helpers.repo_add_remote(tmp_path, "bitbucket", "git@bitbucket.org:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    with pytest.raises(GitUrlError) as exinfo:
        get_git_url(defaultConfig, tmp_path / "README.md")
    assert "Repo has multiple remotes and no upstream" in str(exinfo.value)


def test_core__branch_option_with_detached_head(tmp_path):
    helpers.repo_create(tmp_path, branch="feature-x")
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello 1\n")
    old_hash = helpers.repo_get_current_hash(tmp_path)
    helpers.repo_commit_file(tmp_path, "README.md", "hello 2\n")
    helpers.repo_checkout(tmp_path, old_hash)
    with pytest.raises(GitUrlError) as exinfo:
        get_git_url(defaultConfig, tmp_path / "README.md", branch_mode=True)
    assert "Cannot build a branch-based URL with no branch checked out" in str(exinfo.value)


def test_core__no_matching_config(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", "git@github.acme.corp:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    with pytest.raises(GitUrlError) as exinfo:
        get_git_url(defaultConfig, tmp_path / "README.md")
    assert "No config matched remote URL" in str(exinfo.value)


def test_core__single_remote(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    url = get_git_url(defaultConfig, tmp_path / "README.md")
    hash = helpers.repo_get_current_hash(tmp_path)
    assert url == f"https://github.com/gilessmart/giturl/blob/{hash}/README.md"


def test_core__multiple_remotes_and_upstream(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "github", "git@github.com:gilessmart/giturl.git")
    helpers.repo_add_remote(tmp_path, "bitbucket", "git@bitbucket.org:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    helpers.repo_set_upstream(tmp_path, "github")
    url = get_git_url(defaultConfig, tmp_path / "README.md")
    hash = helpers.repo_get_current_hash(tmp_path)
    assert url == f"https://github.com/gilessmart/giturl/blob/{hash}/README.md"


def test_core__branch_mode(tmp_path):
    helpers.repo_create(tmp_path, branch="feature-x")
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    url = get_git_url(defaultConfig, tmp_path / "README.md", branch_mode=True)
    assert url == f"https://github.com/gilessmart/giturl/blob/feature-x/README.md"


def test_core__branch_mode_with_multiple_remotes_and_upstream(tmp_path):
    helpers.repo_create(tmp_path, "local_branch")
    helpers.repo_add_remote(tmp_path, "github", "git@github.com:gilessmart/giturl.git")
    helpers.repo_add_remote(tmp_path, "bitbucket", "git@bitbucket.org:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    # use a different name for the local and upstream branches
    # so we can tell the upstream branch name is being used
    helpers.repo_set_upstream(tmp_path, "github", "remote_branch")
    url = get_git_url(defaultConfig, tmp_path / "README.md", branch_mode=True)
    assert url == "https://github.com/gilessmart/giturl/blob/remote_branch/README.md"


def test_core__line_num_option(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    url = get_git_url(defaultConfig, tmp_path / "README.md", 7)
    hash = helpers.repo_get_current_hash(tmp_path)
    assert url == f"https://github.com/gilessmart/giturl/blob/{hash}/README.md#L7"


def test_core__root_level_folder(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    url = get_git_url(defaultConfig, tmp_path)
    hash = helpers.repo_get_current_hash(tmp_path)
    assert url == f"https://github.com/gilessmart/giturl/blob/{hash}"


def test_core__root_level_file(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    url = get_git_url(defaultConfig, tmp_path / "README.md")
    hash = helpers.repo_get_current_hash(tmp_path)
    assert url == f"https://github.com/gilessmart/giturl/blob/{hash}/README.md"


def test_core__nested_folder(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_commit_file(tmp_path, "a/b/foo.txt", "hello\n")
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    url = get_git_url(defaultConfig, tmp_path / "a/b")
    hash = helpers.repo_get_current_hash(tmp_path)
    assert url == f"https://github.com/gilessmart/giturl/blob/{hash}/a/b"


def test_core__nested_file(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_commit_file(tmp_path, "a/b/foo.txt", "hello\n")
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    url = get_git_url(defaultConfig, tmp_path / "a/b/foo.txt")
    hash = helpers.repo_get_current_hash(tmp_path)
    assert url == f"https://github.com/gilessmart/giturl/blob/{hash}/a/b/foo.txt"


def test_core__path_with_special_chars(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "file -=+.txt", "hello\n")
    url = get_git_url(defaultConfig, tmp_path / "file -=+.txt")
    hash = helpers.repo_get_current_hash(tmp_path)
    assert url == f"https://github.com/gilessmart/giturl/blob/{hash}/file%20-%3D%2B.txt"


def test_core__local_branch_with_special_chars(tmp_path):
    helpers.repo_create(tmp_path, branch="test-branches/_=+,.@¬£")
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    url = get_git_url(defaultConfig, tmp_path / "README.md", branch_mode=True)
    assert url == f"https://github.com/gilessmart/giturl/blob/test-branches/_%3D%2B%2C.%40%C2%AC%C2%A3/README.md"


def test_core__upstream_branch_with_special_chars(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    helpers.repo_set_upstream(tmp_path, "origin", "test-branches/_=+,.@¬£")
    url = get_git_url(defaultConfig, tmp_path / "README.md", branch_mode=True)
    assert url == f"https://github.com/gilessmart/giturl/blob/test-branches/_%3D%2B%2C.%40%C2%AC%C2%A3/README.md"
