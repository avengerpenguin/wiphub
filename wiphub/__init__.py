import os

from github import Github
from github.Notification import Notification
from github.PullRequest import PullRequest

github = Github(os.getenv("GITHUB_TOKEN"))


def notifications() -> [Notification]:
    yield from github.get_user().get_notifications()


def pulls(team=None) -> [PullRequest]:
    if team:
        for t in github.get_user().get_teams():
            if t.slug == team:
                for r in t.get_repos():
                    if not r.archived:
                        yield from r.get_pulls()
    else:
        for r in github.get_user().get_repos():
            if not r.archived:
                yield from r.get_pulls()
