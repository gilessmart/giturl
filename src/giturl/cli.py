import argparse
import pathlib
import tomllib

from platformdirs import user_config_path

from giturl.app import get_git_url
from giturl.urlgen import ForgeType


default_forges: dict[str, ForgeType] = {
    "github.com": ForgeType.GitHub,
    "bitbucket.org": ForgeType.BitBucket,
    "gitlab.com": ForgeType.GitLab
}


def get_forge_config() -> dict[str, ForgeType]:
    config_file_path = user_config_path("giturl") / "config.toml"
    if not config_file_path.exists():
        return default_forges
    
    try:
        with config_file_path.open("rb") as f:
            raw_config = tomllib.load(f)
    except tomllib.TOMLDecodeError:
        raise Exception("Config file was not valid TOML")
    except OSError:
        raise Exception("Could not read config file")
    
    raw_forges = raw_config.get("forges", {})
    if not isinstance(raw_forges, dict):
        raise Exception("Invalid config - 'forges' was not a table")
    
    forges = {}
    for key, val in raw_forges.items():
        valid_forge_names = [t.name for t in ForgeType]
        if not isinstance(val, str) or not val in valid_forge_names:
            raise Exception(f"Invalid forge type for host '{key}' in config - expected one of {valid_forge_names}, found '{val}'")
        forges[key] = ForgeType[val]
    
    return default_forges | forges


def main():
    parser = argparse.ArgumentParser(description="Generate a GitHub URL for a file or directory in a git repository.")
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
