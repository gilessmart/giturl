from dataclasses import dataclass
import re


@dataclass
class RemoteUrl:
    raw: str
    host: str
    path: str

    # The parsing here doesn't get anywhere near supporting all the valid git remote URLs,
    # and it has no support for URL decoding, but hopefully it can manage the github.com, 
    # bitbucket.org and gitlab.com URLs that it's intended for.
    @staticmethod
    def parse(s: str) -> RemoteUrl:
        patterns = [
            r"git@(?P<host>[\w\.]*\w+):(?P<path>.+)",
            r"https://(.+@)?(?P<host>[\w\.]*\w+)(?P<path>.+)"
        ]

        for pattern in patterns:
            match = re.match(pattern, s)
            if match is not None:
                return RemoteUrl(s, match["host"], match["path"].removeprefix("/"))
        
        raise ValueError(f"remote URL {s} did not match any supported pattern")
