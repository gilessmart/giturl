import os
import subprocess


def repo_create(repo_dir, branch="main"):
    subprocess.check_call(["git", "init", "-b", branch], cwd=repo_dir)
    subprocess.check_call(["git", "config", "user.name", "Test User"], cwd=repo_dir)
    subprocess.check_call(["git", "config", "user.email", "test@example.com"], cwd=repo_dir)


def repo_checkout(repo_dir, ref):
    subprocess.check_call(["git", "checkout", ref], cwd=repo_dir)


def repo_add_remote(repo_dir, name, url):
    subprocess.check_call(["git", "remote", "add", name, url], cwd=repo_dir)


def repo_set_upstream(repo_dir, remote="origin", branch="main"):
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
