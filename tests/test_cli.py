import subprocess
import sys

import helpers


def giturl(*args):
    cmd = [sys.executable, "-m", "giturl", *args]
    return subprocess.run(cmd, capture_output=True, text=True)


def test_cli__github(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    hash = helpers.repo_get_current_hash(tmp_path)
    
    proc = giturl(tmp_path / "README.md")
    assert proc.returncode == 0
    assert proc.stdout.strip() == f"https://github.com/gilessmart/giturl/blob/{hash}/README.md"

    proc = giturl("-l", "7", tmp_path / "README.md")
    assert proc.returncode == 0
    assert proc.stdout.strip() == f"https://github.com/gilessmart/giturl/blob/{hash}/README.md#L7"

    proc = giturl("-b", tmp_path / "README.md")
    assert proc.returncode == 0
    assert proc.stdout.strip() == "https://github.com/gilessmart/giturl/blob/main/README.md"


def test_cli__bitbucket(tmp_path):
    helpers.repo_create(tmp_path)
    helpers.repo_add_remote(tmp_path, "origin", "git@bitbucket.org:gilessmart/giturl.git")
    helpers.repo_commit_file(tmp_path, "README.md", "hello\n")
    hash = helpers.repo_get_current_hash(tmp_path)
    
    proc = giturl(tmp_path / "README.md")
    assert proc.returncode == 0
    assert proc.stdout.strip() == f"https://bitbucket.org/gilessmart/giturl/src/{hash}/README.md"

    proc = giturl("-l", "5", tmp_path / "README.md")
    assert proc.returncode == 0
    assert proc.stdout.strip() == f"https://bitbucket.org/gilessmart/giturl/src/{hash}/README.md#line-5"

    proc = giturl("-b", tmp_path / "README.md")
    assert proc.returncode == 0
    assert proc.stdout.strip() == "https://bitbucket.org/gilessmart/giturl/src/main/README.md"
