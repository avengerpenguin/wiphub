import os

from github import Github
from github.Notification import Notification

github = Github(os.getenv("GITHUB_TOKEN"))


def notifications() -> [Notification]:
    for n in github.get_user().get_notifications():
        yield n
