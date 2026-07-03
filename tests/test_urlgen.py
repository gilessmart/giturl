import pytest

from giturl.types import RefType, UsageError
from giturl.urlgen import get_git_url
from giturl.config import default_forges
import helpers


def test__get_git_url__no_such_file(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    with pytest.raises(UsageError) as exinfo:
        get_git_url(default_forges, tmp_path / "READYOU.md", None, RefType.ShortHash)
    assert "path is not an existing file or directory" in str(exinfo.value)


def test__get_git_url__line_number_with_directory_path(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    with pytest.raises(UsageError) as exinfo:
        get_git_url(default_forges, tmp_path, 20, RefType.ShortHash)
    assert "line number is invalid when the path is a directory" in str(exinfo.value)


def test__get_git_url__no_repo(tmp_path):
    with pytest.raises(UsageError) as exinfo:
        get_git_url(default_forges, tmp_path, None, RefType.ShortHash)
    assert "not part of a git repo" in str(exinfo.value)


def test__get_git_url__path_not_in_index(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    helpers.write_file(tmp_path / "main.c", "#include <stdio.h>")
    with pytest.raises(UsageError) as exinfo:
        get_git_url(default_forges, tmp_path / "main.c", None, RefType.ShortHash)
    assert "not in the git index" in str(exinfo.value)


def test__get_git_url__repo_with_no_commits(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    helpers.write_file(tmp_path / "README.md" , "hello\n")
    with pytest.raises(UsageError) as exinfo:
        get_git_url(default_forges, tmp_path / "README.md", None, RefType.ShortHash)
    assert "not in the git index" in str(exinfo.value)


def test__get_git_url__no_remotes(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    with pytest.raises(UsageError) as exinfo:
        get_git_url(default_forges, tmp_path / "README.md", None, RefType.ShortHash)
    assert "cannot generate URL for repo with no remotes" in str(exinfo.value)


def test__get_git_url__no_upstream_multiple_remotes(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "github", "git@github.com:gilessmart/giturl.git")
    helpers.repo_add_remote(tmp_path, "bitbucket", "git@bitbucket.org:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    with pytest.raises(UsageError) as exinfo:
        get_git_url(default_forges, tmp_path / "README.md", None, RefType.ShortHash)
    assert "cannot generate URL for repo with multiple remotes but no upstream" in str(exinfo.value)


def test__get_git_url__local_remote_url(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    helpers.repo_add_remote(tmp_path, "origin", "file:///Users/giles/repos/giturl")
    with pytest.raises(UsageError) as exinfo:
        get_git_url(default_forges, tmp_path, None, RefType.ShortHash)
    assert "remote URL file:///Users/giles/repos/giturl is unsupported" in str(exinfo.value)


def test__get_git_url__no_matching_config(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", "git@github.acme.corp:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    with pytest.raises(UsageError) as exinfo:
        get_git_url(default_forges, tmp_path / "README.md", None, RefType.ShortHash)
    assert "remote URL host github.acme.corp is not configured" in str(exinfo.value)


def test__get_git_url__ref_type_branch__detached_head(tmp_path):
    helpers.repo_create(tmp_path, branch="feature-x")
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello 1\n")
    old_hash = helpers.repo_get_current_hash(tmp_path)
    helpers.repo_commit_file(tmp_path, "README.md", "hello 2\n")
    helpers.repo_checkout(tmp_path, old_hash)
    with pytest.raises(UsageError) as exinfo:
        get_git_url(default_forges, tmp_path / "README.md", None, RefType.Branch)
    assert "cannot build a branch-based URL with no branch checked out" in str(exinfo.value)


def test__get_git_url__single_remote(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    url = get_git_url(default_forges, tmp_path / "README.md", None, RefType.ShortHash)
    hash = helpers.repo_get_current_hash(tmp_path)
    assert url == f"https://github.com/gilessmart/giturl/blob/{hash}/README.md"


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
    url = get_git_url(default_forges, tmp_path / "README.md", None, RefType.ShortHash)
    hash = helpers.repo_get_current_hash(tmp_path)
    assert url == expected_web_url.format(hash=hash)


def test__get_git_url__ref_type_branch(tmp_path):
    helpers.repo_create(tmp_path, branch="feature-x")
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    url = get_git_url(default_forges, tmp_path / "README.md", None, RefType.Branch)
    assert url == "https://github.com/gilessmart/giturl/blob/feature-x/README.md"


@pytest.mark.parametrize("remote_name, expected_web_url", [
    ("github", "https://github.com/gilessmart/giturl/blob/remote_branch/README.md"),
    ("bitbucket", "https://bitbucket.org/gilessmart/giturl/src/remote_branch/README.md"),
    ("gitlab", "https://gitlab.com/gilessmart/giturl/-/blob/remote_branch/README.md?ref_type=heads")
])
def test__get_git_url__ref_type_branch_with_multiple_remotes_and_upstream(tmp_path, remote_name, expected_web_url):
    helpers.repo_create(tmp_path, "local_branch")
    helpers.repo_add_remote(tmp_path, "github", "git@github.com:gilessmart/giturl.git")
    helpers.repo_add_remote(tmp_path, "bitbucket", "git@bitbucket.org:gilessmart/giturl.git")
    helpers.repo_add_remote(tmp_path, "gitlab", "git@gitlab.com:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    # use a different name for the local and upstream branches
    # so we can tell the upstream branch name is being used
    helpers.repo_set_upstream(tmp_path, remote_name, "remote_branch")
    url = get_git_url(default_forges, tmp_path / "README.md", None, RefType.Branch)
    assert url == expected_web_url


def test__get_git_url__line_number(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    url = get_git_url(default_forges, tmp_path / "README.md", 7, RefType.ShortHash)
    hash = helpers.repo_get_current_hash(tmp_path)
    assert url == f"https://github.com/gilessmart/giturl/blob/{hash}/README.md#L7"


def test__get_git_url__root_level_folder(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    url = get_git_url(default_forges, tmp_path, None, RefType.ShortHash)
    hash = helpers.repo_get_current_hash(tmp_path)
    assert url == "https://github.com/gilessmart/giturl/tree/{hash}/".format(hash=hash)
