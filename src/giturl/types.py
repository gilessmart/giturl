from dataclasses import dataclass
from enum import Enum, auto


class ForgeType(Enum):
    GitHub = auto()
    BitBucket = auto()
    GitLab = auto()


class RefType(Enum):
    Branch = auto()
    CommitHash = auto()


@dataclass
class Ref:
    type: RefType
    value: str
