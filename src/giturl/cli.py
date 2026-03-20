import argparse
import os
import pathlib
import re
import sys
from urllib.parse import quote

import giturl.git as git
from giturl.url_templates import parse_template


def parse_args() -> tuple[str, int | None, bool | None]:
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


url_configs = {
    r"github.com[:/](?P<account>.+?)/(?P<repo>.+?).git": "https://github.com/{{account}}/{{repo}}/blob/{{ref}}{{path}}{#L{line_number}}",
    r"bitbucket.org[:/](?P<account>.+?)/(?P<repo>.+?).git": "https://bitbucket.org/{{account}}/{{repo}}/src/{{ref}}{{path}}{#line-{line_number}}",
}


def generate_url(remote_url: str, url_args: dict) -> str:
    for pattern, template_str in url_configs.items():
        match = re.search(pattern, remote_url)
        if match:
            template = parse_template(template_str)
            return template.apply(match.groupdict() | url_args)
    
    print(f"Error: No config matched remote URL {remote_url}", file=sys.stderr)
    sys.exit(1)


def main():
    path_arg, line_number, branch_mode = parse_args()

    full_path = os.path.abspath(path_arg)

    repo_root = git.get_repo_root(full_path)
    if repo_root is None:
        print(f"Error: Path '{full_path}' is not part of a git repo.", file=sys.stderr)
        sys.exit(1)

    remotes = git.get_remotes(repo_root)
    if not remotes:
        print("Error: No git remotes in this repo.", file=sys.stderr)
        sys.exit(1)
    
    local_branch = git.get_current_branch_name(repo_root)

    if branch_mode:
        if local_branch is None:
            print("Error: Cannot build a branch-based URL with no branch checked out.", file=sys.stderr)
            sys.exit(1)
        upstream_branch = git.get_upstream_branch(repo_root, local_branch)
        ref = quote(upstream_branch or local_branch)
    else:
        ref = git.get_short_hash(repo_root)
        if ref is None:
            print("Error: Unable to fetch the latest commit hash. Does the repo have any commits?", file=sys.stderr)
            sys.exit(1)

    remote = git.get_upstream_remote(repo_root, local_branch) if local_branch else None
    if remote is None:
        if len(remotes) == 1:
            remote = remotes[0]
        else:
            print("Error: Repo has multiple remotes and no upstream to determine the correct one.", file=sys.stderr)
            sys.exit(1)
    
    remote_url = git.get_remote_url(repo_root, remote)

    if os.path.samefile(full_path, repo_root):
        relative_path = ""
    else:
        relative_path = "/" + quote(os.path.relpath(full_path, repo_root).replace(os.sep, "/"))

    url = generate_url(remote_url, {
        "ref": ref,
        "path": relative_path,
        "line_number": str(line_number) if line_number is not None else None,
    })

    print(url)
