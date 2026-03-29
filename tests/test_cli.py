import subprocess
import sys

import helpers


def giturl(*args):
    cmd = [sys.executable, "-m", "giturl", *args]
    return subprocess.run(cmd, capture_output=True, text=True)


def test_cli__github(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:my-account/my-repo.git")
    helpers.repo_commit_file(tmp_path, "subdir/info.txt", "hello\n")
    hash = helpers.repo_get_current_hash(tmp_path)

    # file path
    proc = giturl(tmp_path / "subdir/info.txt")
    assert proc.returncode == 0
    assert proc.stdout.strip() == f"https://github.com/my-account/my-repo/blob/{hash}/subdir/info.txt"

    # folder path
    proc = giturl(tmp_path / "subdir")
    assert proc.returncode == 0
    assert proc.stdout.strip() == f"https://github.com/my-account/my-repo/blob/{hash}/subdir"

    # line number
    proc = giturl("-l", "7", tmp_path / "subdir/info.txt")
    assert proc.returncode == 0
    assert proc.stdout.strip() == f"https://github.com/my-account/my-repo/blob/{hash}/subdir/info.txt#L7"

    # branch mode
    proc = giturl("-b", tmp_path / "subdir/info.txt")
    assert proc.returncode == 0
    assert proc.stdout.strip() == "https://github.com/my-account/my-repo/blob/main/subdir/info.txt"


def test_cli__bitbucket(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", "git@bitbucket.org:my-account/my-repo.git")
    helpers.repo_commit_file(tmp_path, "subdir/info.txt", "hello\n")
    hash = helpers.repo_get_current_hash(tmp_path)

    # file path
    proc = giturl(tmp_path / "subdir/info.txt")
    assert proc.returncode == 0
    assert proc.stdout.strip() == f"https://bitbucket.org/my-account/my-repo/src/{hash}/subdir/info.txt"

    # folder path
    proc = giturl(tmp_path / "subdir")
    assert proc.returncode == 0
    assert proc.stdout.strip() == f"https://bitbucket.org/my-account/my-repo/src/{hash}/subdir"

    # line number
    proc = giturl("-l", "5", tmp_path / "subdir/info.txt")
    assert proc.returncode == 0
    assert proc.stdout.strip() == f"https://bitbucket.org/my-account/my-repo/src/{hash}/subdir/info.txt#line-5"

    # branch mode
    proc = giturl("-b", tmp_path / "subdir/info.txt")
    assert proc.returncode == 0
    assert proc.stdout.strip() == "https://bitbucket.org/my-account/my-repo/src/main/subdir/info.txt"


def test_cli__gitlab(tmp_path):
    # Repo at https://gitlab.com/gitlab-org/gitlab used to determine requirements

    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", "git@gitlab.com:my-org/my-project.git")
    helpers.repo_commit_file(tmp_path, "subdir/info.txt", "hello\n")
    hash = helpers.repo_get_current_hash(tmp_path)
    
    # file path
    proc = giturl(tmp_path / "subdir/info.txt")
    assert proc.returncode == 0
    assert proc.stdout.strip() == f"https://gitlab.com/my-org/my-project/-/blob/{hash}/subdir/info.txt"

    # folder path - not supported
    # proc = giturl(tmp_path / "subdir")
    # assert proc.returncode == 0
    # assert proc.stdout.strip() == f"https://gitlab.com/my-org/my-project/-/tree/{hash}/subdir"

    # line number
    proc = giturl("-l", "10", tmp_path / "subdir/info.txt")
    assert proc.returncode == 0
    assert proc.stdout.strip() == f"https://gitlab.com/my-org/my-project/-/blob/{hash}/subdir/info.txt#L10"

    # branch mode - query string not supported
    # proc = giturl("-b", tmp_path / "subdir/info.txt")
    # assert proc.returncode == 0
    # assert proc.stdout.strip() == "https://gitlab.com/my-org/my-project/-/blob/main/subdir/info.txt?ref_type=heads"

def test_cli__gitlab_subproject(tmp_path):
    # Repo at https://gitlab.com/gitlab-org/ai/skills used to determine requirements

    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", "git@gitlab.com:my-org/project/sub-project.git")
    helpers.repo_commit_file(tmp_path, "subdir/info.txt", "hello\n")
    hash = helpers.repo_get_current_hash(tmp_path)
    
    # file path
    proc = giturl(tmp_path / "subdir/info.txt")
    assert proc.returncode == 0
    assert proc.stdout.strip() == f"https://gitlab.com/my-org/project/sub-project/-/blob/{hash}/subdir/info.txt"

    # folder path - not supported
    # proc = giturl(tmp_path / "subdir")
    # assert proc.returncode == 0
    # assert proc.stdout.strip() == f"https://gitlab.com/my-org/project/sub-project/-/tree/{hash}/subdir"

    # line number
    proc = giturl("-l", "10", tmp_path / "subdir/info.txt")
    assert proc.returncode == 0
    assert proc.stdout.strip() == f"https://gitlab.com/my-org/project/sub-project/-/blob/{hash}/subdir/info.txt#L10"

    # branch mode - query string not supported
    # proc = giturl("-b", tmp_path / "subdir/info.txt")
    # assert proc.returncode == 0
    # assert proc.stdout.strip() == "https://gitlab.com/my-org/project/sub-project/-/blob/main/subdir/info.txt?ref_type=heads"
