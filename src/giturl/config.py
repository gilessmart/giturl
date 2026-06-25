import tomllib

from platformdirs import user_config_path

from giturl.weburl import ForgeType


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