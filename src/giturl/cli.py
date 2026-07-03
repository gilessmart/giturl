import argparse
import pathlib

from giturl.types import ConfigError, RefType, UsageError
from giturl.urlgen import get_git_url
from giturl.config import get_forge_config


def main():
    parser = argparse.ArgumentParser(description="Generates a website URL for a path that's part of a repo hosted on a GitHub, BitBucket or GitLab git forge.")
    parser.add_argument("-l", "--line-number", dest="line_number", type=int, help="Line number to include in the URL", metavar="line_number")
    parser.add_argument("-r", "--ref-type", dest="ref_type", type=RefType.parse, help=f"Git ref type to use in the constructed URL - valid values: {str.join(", ", [t.name.lower() for t in RefType])}", metavar="ref_type", default=RefType.ShortHash)
    parser.add_argument("path", type=pathlib.Path, help="Path to a file or directory in a git repository")
    args = parser.parse_args()

    try:
        forge_config = get_forge_config()
        url = get_git_url(forge_config, args.path, args.line_number, args.ref_type)
    except ConfigError as e:
        print(f"Config error - {e}")
        exit(1)
    except UsageError as e:
        parser.error(str(e))

    print(url)
