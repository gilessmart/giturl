import argparse
import pathlib

from giturl.core import get_git_url, GitUrlError


config = {
    r"github.com[:/](?P<account>.+?)/(?P<repo>.+?).git": "https://github.com/{{account}}/{{repo}}/blob/{{ref}}{{path}}{#L{line_number}}",
    r"bitbucket.org[:/](?P<account>.+?)/(?P<repo>.+?).git": "https://bitbucket.org/{{account}}/{{repo}}/src/{{ref}}{{path}}{#line-{line_number}}",
}


def main():
    parser = argparse.ArgumentParser(description="Generate a GitHub URL for a file or directory in a git repository.")
    parser.add_argument("-l", "--line", dest="line_number", type=int, help="Line number to include in the URL", metavar="line_number")
    parser.add_argument("-b", "--branch", dest="branch_mode", action="store_true", help="Use branch name instead of commit SHA in the URL")
    parser.add_argument("path", type=pathlib.Path, help="Path to a file or directory in the git repository")
    args = parser.parse_args()

    try:
        url = get_git_url(config, args.path, args.line_number, args.branch_mode)
        print(url)
    except GitUrlError as e:
        parser.error(str(e))
