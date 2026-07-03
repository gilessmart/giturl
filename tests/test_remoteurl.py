from giturl.remoteurl import RemoteUrl


def test__RemoteUrl__parse__github_ssh():
    result = RemoteUrl.parse("git@github.com:gilessmart/giturl.git")
    assert result.host == "github.com"
    assert result.path == "gilessmart/giturl.git"


def test__RemoteUrl__parse__github_https():
    result = RemoteUrl.parse("https://github.com/gilessmart/giturl.git")
    assert result.host == "github.com"
    assert result.path == "gilessmart/giturl.git"


def test__RemoteUrl__parse__bitbucket_ssh():
    result = RemoteUrl.parse("git@bitbucket.org:gilessmart/giturl.git")
    assert result.host == "bitbucket.org"
    assert result.path == "gilessmart/giturl.git"


def test__RemoteUrl__parse__bitbucket_https():
    result = RemoteUrl.parse("https://gilessmart@bitbucket.org/gilessmart/giturl.git")
    assert result.host == "bitbucket.org"
    assert result.path == "gilessmart/giturl.git"


def test__RemoteUrl__parse__gitlab_ssh():
    result = RemoteUrl.parse("git@gitlab.com:gitlab-org/gitlab.git")
    assert result.host == "gitlab.com"
    assert result.path == "gitlab-org/gitlab.git"


def test__RemoteUrl__parse__gitlab_https():
    result = RemoteUrl.parse("https://gitlab.com/gitlab-org/gitlab.git")
    assert result.host == "gitlab.com"
    assert result.path == "gitlab-org/gitlab.git"


def test__RemoteUrl__parse__gitlab_subproject_ssh():
    result = RemoteUrl.parse("git@gitlab.com:gitlab-org/ai/skills.git")
    assert result.host == "gitlab.com"
    assert result.path == "gitlab-org/ai/skills.git"


def test__RemoteUrl__parse__gitlab_subproject_https():
    result = RemoteUrl.parse("https://gitlab.com/gitlab-org/ai/skills.git")
    assert result.host == "gitlab.com"
    assert result.path == "gitlab-org/ai/skills.git"
