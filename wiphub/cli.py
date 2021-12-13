import os
from github.Notification import Notification
from github.PullRequest import PullRequest
from git import Repo
from yarl import URL
import tempfile
from . import notifications


def _rebase(pr: PullRequest):
    with tempfile.TemporaryDirectory() as wd:
        url = str(URL(
            pr.base.repo.clone_url
        ).with_user(os.getenv("GITHUB_TOKEN")).with_password('x-oauth-basic'))

        repo: Repo = Repo.clone_from(url, wd, branch=pr.head.ref)

        repo.git.rebase(f'origin/{pr.base.repo.default_branch}')
        print(f'Want to rebase {pr} {pr.base.repo} with {repo}')
        
        proceed = input("Push? (y/n) ")
        if proceed == "y":
            pr.merge()


def _handle_pr(pr: PullRequest):
    match pr.raw_data:
        case {"state": "closed"}:
            print(f'"{pr.title}" -- closed, so ignoring -- see {pr.html_url}')
        case {"mergeable_state": "clean"}:
            print(f'"{pr.title}" -- state {pr.mergeable_state} -- will be merged -- see {pr.html_url}')
            proceed = input("Merge? (y/n) ")
            if proceed == "y":
                pr.merge()
            else:
                exit()
        case {"mergeable_state": "behind"}:
            _rebase(pr)
        case _:
            print(f'"{pr.title}" -- state {pr.mergeable_state} -- needs your attention -- see {pr.html_url}')
            exit()


def _clear_issue_notification(n: Notification):
    issue = n.get_issue()
    match issue.raw_data:
        case {"state": "closed"}:
            print(f'"{issue.title}" -- closed, so marking as read -- see {issue.html_url}')
            n.mark_as_read()
        case _:
            print(f'"{issue.title}" -- needs your attention -- see {issue.html_url}')
            exit()


def _clear_notifications():
    for n in notifications():
        match n.raw_data:
            case {"subject": {"type": "PullRequest"}}:
                _handle_pr(n.get_pull_request())
                n.mark_as_read()
            case {"subject": {"type": "Issue"}}:
                _clear_issue_notification(n)
            case _:
                raise KeyError(f"Unrecognised notification type: {n.raw_data}")


def main():
    _clear_notifications()


if __name__ == "__main__":
    main()
