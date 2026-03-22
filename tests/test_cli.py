import os
import subprocess
import sys


def repo_create(repo_dir, branch="main"):
    subprocess.check_call(["git", "init", "-b", branch], cwd=repo_dir)
    subprocess.check_call(["git", "config", "user.name", "Test User"], cwd=repo_dir)
    subprocess.check_call(["git", "config", "user.email", "test@example.com"], cwd=repo_dir)


def repo_checkout(repo_dir, ref):
    subprocess.check_call(["git", "checkout", ref], cwd=repo_dir)


def repo_add_remote(repo_dir, name, url):
    subprocess.check_call(["git", "remote", "add", name, url], cwd=repo_dir)


def repo_set_upstream(repo_dir, remote, branch):
    subprocess.check_call(["git", "update-ref", f"refs/remotes/{remote}/{branch}", "HEAD"], cwd=repo_dir)
    subprocess.check_call(["git", "branch", f"--set-upstream-to={remote}/{branch}"], cwd=repo_dir)


def repo_commit_file(repo_dir, file_path, content):
    write_file(repo_dir / file_path, content)
    subprocess.check_call(["git", "add", file_path], cwd=repo_dir)
    subprocess.check_call(["git", "commit", "-m", f"Add {file_path}"], cwd=repo_dir)


def write_file(file_path, content):
    dir = os.path.dirname(file_path)
    os.makedirs(dir, exist_ok=True)
    with open(file_path, "w") as file:
        file.write(content)


def repo_get_current_hash(repo_dir):
    return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=repo_dir, text=True).strip()


def giturl(*args):
    cmd = [sys.executable, "-m", "giturl", *args]
    return subprocess.run(cmd, capture_output=True, text=True)


def test_cli__no_repo(tmp_path):
    proc = giturl(tmp_path)
    assert proc.returncode == 1
    assert "not part of a git repo" in proc.stderr


def test_cli__no_remotes(tmp_path):
    repo_create(tmp_path)
    repo_commit_file(tmp_path, "README.md", "hello\n")
    proc = giturl(tmp_path / "README.md")
    assert proc.returncode == 1
    assert "No git remotes" in proc.stderr


def test_cli__no_upstream_multiple_remotes(tmp_path):
    repo_create(tmp_path)
    repo_add_remote(tmp_path, "github", "git@github.com:gilessmart/giturl.git")
    repo_add_remote(tmp_path, "bitbucket", "git@bitbucket.org:gilessmart/giturl.git")
    repo_commit_file(tmp_path, "README.md", "hello\n")
    proc = giturl(tmp_path)
    assert proc.returncode == 1
    assert "multiple remotes" in proc.stderr


def test_cli__with_upstream_and_multiple_remotes(tmp_path):
    repo_create(tmp_path, "local_branch")
    repo_add_remote(tmp_path, "github", "git@github.com:gilessmart/giturl.git")
    repo_add_remote(tmp_path, "bitbucket", "git@bitbucket.org:gilessmart/giturl.git")
    repo_commit_file(tmp_path, "README.md", "hello\n")
    repo_set_upstream(tmp_path, "github", "remote_branch")
    proc = giturl("-b", tmp_path / "README.md")
    assert proc.returncode == 0
    assert proc.stdout.strip() == f"https://github.com/gilessmart/giturl/blob/remote_branch/README.md"


def test_cli__upstream_and_remote_name_with_special_chars(tmp_path):
    repo_create(tmp_path, "local_branch")
    repo_add_remote(tmp_path, "remote-/_=+,.@¬£", "git@github.com:gilessmart/giturl.git")
    repo_commit_file(tmp_path, "README.md", "hello\n")
    repo_set_upstream(tmp_path, "remote-/_=+,.@¬£", "remote_branch")
    proc = giturl("-b", tmp_path / "README.md")
    assert proc.returncode == 0
    assert proc.stdout.strip() == f"https://github.com/gilessmart/giturl/blob/remote_branch/README.md"


def test_cli__no_upstream_single_remote(tmp_path):
    repo_create(tmp_path, "branch_name")
    repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    repo_commit_file(tmp_path, "README.md", "hello\n")
    proc = giturl("-b", tmp_path / "README.md")
    assert proc.returncode == 0
    assert proc.stdout.strip() == f"https://github.com/gilessmart/giturl/blob/branch_name/README.md"


def test_cli__root_level_folder(tmp_path):
    repo_create(tmp_path)
    repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    repo_commit_file(tmp_path, "README.md", "hello\n")
    hash = repo_get_current_hash(tmp_path)
    proc = giturl(tmp_path)
    assert proc.returncode == 0
    assert proc.stdout.strip() == f"https://github.com/gilessmart/giturl/blob/{hash}"


def test_cli__root_level_file(tmp_path):
    repo_create(tmp_path)
    repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    repo_commit_file(tmp_path, "README.md", "hello\n")
    hash = repo_get_current_hash(tmp_path)
    proc = giturl(tmp_path / "README.md")
    assert proc.returncode == 0
    assert proc.stdout.strip() == f"https://github.com/gilessmart/giturl/blob/{hash}/README.md"


def test_cli__path_doesnt_exist(tmp_path):
    repo_create(tmp_path)
    repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    repo_commit_file(tmp_path, "README.md", "hello\n")
    proc = giturl(tmp_path / "READYOU.md")
    assert proc.returncode != 0
    assert "not an existing file or directory" in proc.stderr


def test_cli__file_not_in_repo(tmp_path):
    repo_create(tmp_path)
    repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    repo_commit_file(tmp_path, "README.md", "hello\n")
    write_file(tmp_path / "READYOU.md", "goodbye\n")    
    proc = giturl(tmp_path / "READYOU.md")
    assert proc.returncode != 0
    assert "not in the git tree" in proc.stderr


def test_cli__nested_file(tmp_path):
    repo_create(tmp_path)
    repo_commit_file(tmp_path, "a/b/foo.txt", "hello\n")
    repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    hash = repo_get_current_hash(tmp_path)
    proc = giturl(tmp_path / "a/b/foo.txt")
    assert proc.returncode == 0
    assert proc.stdout.strip() == f"https://github.com/gilessmart/giturl/blob/{hash}/a/b/foo.txt"


def test_cli__line_num_option(tmp_path):
    repo_create(tmp_path)
    repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    repo_commit_file(tmp_path, "README.md", "hello\n")
    hash = repo_get_current_hash(tmp_path)
    proc = giturl("-l", "7", tmp_path / "README.md")
    assert proc.returncode == 0
    assert proc.stdout.strip() == f"https://github.com/gilessmart/giturl/blob/{hash}/README.md#L7"


def test_cli__branch_option(tmp_path):
    repo_create(tmp_path, branch="feature-x")
    repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    repo_commit_file(tmp_path, "README.md", "hello\n")
    proc = giturl("-b", tmp_path / "README.md")
    assert proc.returncode == 0
    assert proc.stdout.strip() == f"https://github.com/gilessmart/giturl/blob/feature-x/README.md"


def test_cli__branch_option_with_detached_head(tmp_path):
    repo_create(tmp_path, branch="feature-x")
    repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    repo_commit_file(tmp_path, "README.md", "hello 1\n")
    old_hash = repo_get_current_hash(tmp_path)
    repo_commit_file(tmp_path, "README.md", "hello 2\n")
    repo_checkout(tmp_path, old_hash)
    proc = giturl("-b", tmp_path / "README.md")
    assert proc.returncode != 0
    assert "no branch checked out" in proc.stderr


def test_cli__path_with_special_chars(tmp_path):
    repo_create(tmp_path)
    repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    repo_commit_file(tmp_path, "file -=+.txt", "hello\n")
    hash = repo_get_current_hash(tmp_path)
    proc = giturl(tmp_path / "file -=+.txt")
    assert proc.returncode == 0
    assert proc.stdout.strip() == f"https://github.com/gilessmart/giturl/blob/{hash}/file%20-%3D%2B.txt"


def test_cli__local_branch_with_special_chars(tmp_path):
    repo_create(tmp_path, branch="test-branches/_=+,.@¬£")
    repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    repo_commit_file(tmp_path, "README.md", "hello\n")
    proc = giturl("-b", tmp_path / "README.md")
    assert proc.returncode == 0
    assert proc.stdout.strip() == f"https://github.com/gilessmart/giturl/blob/test-branches/_%3D%2B%2C.%40%C2%AC%C2%A3/README.md"


def test_cli__upstream_branch_with_special_chars(tmp_path):
    repo_create(tmp_path)
    repo_add_remote(tmp_path, "origin", "git@github.com:gilessmart/giturl.git")
    repo_commit_file(tmp_path, "README.md", "hello\n")
    repo_set_upstream(tmp_path, "origin", "test-branches/_=+,.@¬£")
    proc = giturl("-b", tmp_path / "README.md")
    assert proc.returncode == 0
    assert proc.stdout.strip() == f"https://github.com/gilessmart/giturl/blob/test-branches/_%3D%2B%2C.%40%C2%AC%C2%A3/README.md"
