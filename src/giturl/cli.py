import argparse
import pathlib

from giturl.urlgen import get_git_url
from giturl.config import get_forge_config


def main():
    parser = argparse.ArgumentParser(description="Generates a website URL for a path that's part of a repo hosted on a GitHub, BitBucket or GitLab git forge.")
    parser.add_argument("-l", "--line", dest="line_number", type=int, help="Line number to include in the URL", metavar="line_number")
    parser.add_argument("-b", "--branch", dest="branch_mode", action="store_true", help="Use branch name instead of commit SHA in the URL")
    parser.add_argument("path", type=pathlib.Path, help="Path to a file or directory in the git repository")
    args = parser.parse_args()

    try:
        forge_config = get_forge_config()
        url = get_git_url(forge_config, args.path, args.line_number, args.branch_mode)
        print(url)
    except Exception as e:
        parser.error(str(e))
