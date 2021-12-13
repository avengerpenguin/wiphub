import os

from github import Github
from github.Notification import Notification

github = Github(os.getenv("GITHUB_TOKEN"))


def notifications() -> [Notification]:
    yield from github.get_user().get_notifications()
