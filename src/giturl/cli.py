import argparse
import os
import pathlib
import re
import sys
from typing import NoReturn
from urllib.parse import quote

import giturl.git as git
from giturl.url_templates import parse_template


def main():
    path_arg, line_number, branch_mode = parse_args()

    full_path = os.path.abspath(path_arg)

    repo_root = git.get_repo_root(full_path)
    if repo_root is None:
        fail(f"Path '{full_path}' is not part of a git repo.")

    local_branch = git.get_current_branch_name(repo_root)

    remote = get_remote(repo_root, local_branch)
    
    remote_url = git.get_remote_url(repo_root, remote)

    if branch_mode:
        ref = get_branch(repo_root, local_branch)
    else:
        ref = get_short_hash(repo_root)

    path = get_repo_path(repo_root, full_path)

    url = generate_url(remote_url, {
        "ref": ref,
        "path": path,
        "line_number": str(line_number) if line_number is not None else None,
    })

    print(url)


def parse_args() -> tuple[str, int | None, bool]:
    parser = argparse.ArgumentParser(description="Generate a GitHub URL for a file or directory in a git repository.")
    parser.add_argument("-l", "--line", dest="line_number", type=int, help="Line number to include in the URL", metavar="line_number")
    parser.add_argument("-b", "--branch", dest="branch_mode", action="store_true", help="Use branch name instead of commit SHA in the URL")
    parser.add_argument("path", type=pathlib.Path, help="Path to a file or directory in the git repository")
    args = parser.parse_args()
    
    if not os.path.isfile(args.path) and not os.path.isdir(args.path):
        parser.error(f"'{args.path}' is not an existing file or directory")

    if args.line_number is not None and os.path.isdir(args.path):
        parser.error("line number is invalid when path is a directory")
    
    return args.path, args.line_number, args.branch_mode


def fail(msg: str) -> NoReturn:
    print("Error: " + msg, file=sys.stderr)
    sys.exit(1)


def get_ref(repo_root: str, branch_mode: bool, local_branch: str | None):
    return get_branch(repo_root, local_branch) if branch_mode else get_short_hash(repo_root)


def get_remote(repo_root: str, local_branch: str | None) -> str:
    if local_branch is not None and (remote := git.get_upstream_remote(repo_root, local_branch)) is not None:
        return remote
        
    remotes = git.get_remotes(repo_root)
    if len(remotes) == 0:
        fail("No git remotes in this repo.")
    elif len(remotes) == 1:
        return remotes[0]
    else:
        fail("Repo has multiple remotes and no upstream to determine the correct one.")


def get_branch(repo_root: str, local_branch: str | None):
    if local_branch is None:
        fail("Cannot build a branch-based URL with no branch checked out.")
    upstream_branch = git.get_upstream_branch(repo_root, local_branch)
    return upstream_branch or local_branch


def get_short_hash(repo_root: str):
    if (hash := git.get_short_hash(repo_root)) is None:
        fail("Unable to fetch the latest commit hash. Does the repo have any commits?")
    return hash


def get_repo_path(repo_root, full_path):
    if os.path.samefile(full_path, repo_root):
        return ""
    return "/" + os.path.relpath(full_path, repo_root).replace(os.sep, "/")


def generate_url(remote_url: str, url_args: dict[str, str | None]) -> str:
    url_configs = {
        r"github.com[:/](?P<account>.+?)/(?P<repo>.+?).git": "https://github.com/{{account}}/{{repo}}/blob/{{ref}}{{path}}{#L{line_number}}",
        r"bitbucket.org[:/](?P<account>.+?)/(?P<repo>.+?).git": "https://bitbucket.org/{{account}}/{{repo}}/src/{{ref}}{{path}}{#line-{line_number}}",
    }

    for pattern, template_str in url_configs.items():
        match = re.search(pattern, remote_url)
        if match:
            template = parse_template(template_str)
            quoted_args = { k: quote(v) for (k, v) in (match.groupdict() | url_args).items() if v is not None }
            return template.apply(quoted_args)
    
    fail(f"No config matched remote URL {remote_url}")
