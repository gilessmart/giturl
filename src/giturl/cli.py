import argparse
import os
import pathlib

from giturl.core import get_git_url


def main():
    path_arg, line_number, branch_mode = parse_args()
    url = get_git_url(path_arg, line_number, branch_mode)
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
