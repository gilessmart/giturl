from giturl.remoteurl import parse_remote_url


def test__parse_remote_url__github_ssh():
    result = parse_remote_url("git@github.com:gilessmart/giturl.git")
    assert result.host == "github.com"
    assert result.path == "gilessmart/giturl.git"


def test__parse_remote_url__github_https():
    result = parse_remote_url("https://github.com/gilessmart/giturl.git")
    assert result.host == "github.com"
    assert result.path == "gilessmart/giturl.git"


def test__parse_remote_url__bitbucket_ssh():
    result = parse_remote_url("git@bitbucket.org:gilessmart/giturl.git")
    assert result.host == "bitbucket.org"
    assert result.path == "gilessmart/giturl.git"


def test__parse_remote_url__bitbucket_https():
    result = parse_remote_url("https://gilessmart@bitbucket.org/gilessmart/giturl.git")
    assert result.host == "bitbucket.org"
    assert result.path == "gilessmart/giturl.git"


def test__parse_remote_url__gitlab_ssh():
    result = parse_remote_url("git@gitlab.com:gitlab-org/gitlab.git")
    assert result.host == "gitlab.com"
    assert result.path == "gitlab-org/gitlab.git"


def test__parse_remote_url__gitlab_https():
    result = parse_remote_url("https://gitlab.com/gitlab-org/gitlab.git")
    assert result.host == "gitlab.com"
    assert result.path == "gitlab-org/gitlab.git"


def test__parse_remote_url__gitlab_subproject_ssh():
    result = parse_remote_url("git@gitlab.com:gitlab-org/ai/skills.git")
    assert result.host == "gitlab.com"
    assert result.path == "gitlab-org/ai/skills.git"


def test__parse_remote_url__gitlab_subproject_https():
    result = parse_remote_url("https://gitlab.com/gitlab-org/ai/skills.git")
    assert result.host == "gitlab.com"
    assert result.path == "gitlab-org/ai/skills.git"
