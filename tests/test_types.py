import pytest

from giturl.types import RefType


def test__reftype_parse():
    assert RefType.parse("bRaNcH") == RefType.Branch
    assert RefType.parse("ShOrThAsH") == RefType.ShortHash
    with pytest.raises(ValueError):
        RefType.parse("unknown")
