import pytest

from giturl.url_templates import FillPointSegment, parse_template


def test_TemplateParser_apply__github_template__missing_line_number_argument():
    template = parse_template("https://github.com/{{account}}/{{repo}}/blob/{{ref}}{{path}}{#L{line_number}}")
    url = template.apply({
        "account": "gilessmart",
        "repo": "giturl",
        "ref": "main",
        "path": "/src/giturl/cli.py",
    })
    assert url == "https://github.com/gilessmart/giturl/blob/main/src/giturl/cli.py"


def test_TemplateParser_apply__github_template__with_line_number_argument():
    template = parse_template("https://github.com/{{account}}/{{repo}}/blob/{{ref}}{{path}}{#L{line_number}}")
    url = template.apply({
        "account": "gilessmart",
        "repo": "giturl",
        "ref": "main",
        "path": "/src/giturl/cli.py",
        "line_number": "5",
    })
    assert url == "https://github.com/gilessmart/giturl/blob/main/src/giturl/cli.py#L5"


def test_TemplateParser_parse__incomplete_fill_point():
    with pytest.raises(ValueError) as err:
        parse_template("https://github.com/{account}/{repo}/blob/{ref}{pat")
    assert "Unclosed fill point segment in template string" in str(err.value)


def test_TemplateSegment_apply__single_fill_point__argument_given():
    segment = FillPointSegment("{account}", ["account"])
    result = segment.apply({"account": "gilessmart"})
    assert result == "gilessmart"


def test_TemplateSegment_apply__single_fill_point__argument_none():
    segment = FillPointSegment("{account}", ["account"])
    result = segment.apply({"account": None})
    assert result == ""


def test_TemplateSegment_apply__single_fill_point__argument_missing():
    segment = FillPointSegment("{account}", ["account"])
    result = segment.apply({})
    assert result == ""


def test_TemplateSegment_apply__single_fill_point_with_extra_text__argument_given():
    segment = FillPointSegment("acc={account}", ["account"])
    result = segment.apply({"account": "gilessmart"})
    assert result == "acc=gilessmart"


def test_TemplateSegment_apply__single_fill_point_with_extra_text__argument_none():
    segment = FillPointSegment("acc={account}", ["account"])
    result = segment.apply({"account": None})
    assert result == ""


def test_TemplateSegment_apply__single_fill_point_with_extra_text__argument_missing():
    segment = FillPointSegment("acc={account}", ["account"])
    result = segment.apply({})
    assert result == ""
