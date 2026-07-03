from dataclasses import dataclass
from enum import Enum, auto


class ConfigError(Exception): ...


class UsageError(Exception): ...


class ForgeType(Enum):
    GitHub = auto()
    BitBucket = auto()
    GitLab = auto()


class RefType(Enum):
    ShortHash = auto()
    Branch = auto()    

    @staticmethod
    def parse(s: str) -> RefType:
        for t in RefType:
            if t.name.lower() == s.lower():
                return t
        raise ValueError(f"Invalid literal for RefType.parse(): {s}")


@dataclass
class Ref:
    type: RefType
    value: str
