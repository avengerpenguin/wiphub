import os
import tempfile
from collections import defaultdict

import typer
from git import Repo
from github.Notification import Notification
from github.PullRequest import PullRequest
from yarl import URL

from . import github, notifications, pulls


def _rebase(pr: PullRequest):
    with tempfile.TemporaryDirectory() as wd:
        url = str(
            URL(pr.base.repo.clone_url)
            .with_user(os.getenv("GITHUB_TOKEN"))
            .with_password("x-oauth-basic")
        )

        repo: Repo = Repo.clone_from(url, wd, branch=pr.head.ref)

        repo.git.rebase(f"origin/{pr.base.repo.default_branch}")
        print(f"Want to rebase {pr} {pr.base.repo} with {repo}")

        proceed = input("Push? (y/n) ")
        if proceed == "y":
            repo.git.push("--force-with-lease")


def _handle_pr(pr: PullRequest):
    current_user = github.get_user().login
    # print(json.dumps(pr.raw_data, indent=2))
    match pr.raw_data:
        case {"state": "closed"}:
            print(f'"{pr.title}" -- closed, so ignoring -- see {pr.html_url}')
        case {
            "mergeable_state": "clean",
            "draft": False,
            "user": {"login": current_user},
        }:
            print(
                f'"{pr.title}" -- state {pr.mergeable_state} -- will be merged -- see {pr.html_url}'
            )
            proceed = input("Merge? (y/n) ")
            if proceed == "y":
                pr.merge()
            else:
                exit()
        case {
            "mergeable_state": "clean",
            "draft": False,
            "labels": [{"name": "renovate"}, *_],
        }:
            print(
                f'"{pr.title}" -- state {pr.mergeable_state} -- will be merged -- see {pr.html_url}'
            )
            proceed = input("Merge? (y/n) ")
            if proceed == "y":
                pr.merge()
            else:
                exit()
        case {"mergeable_state": "behind", "author": {"login": current_user}}:
            _rebase(pr)
        case _:
            print(
                f'"{pr.title}" -- state {pr.mergeable_state} -- needs your attention -- see {pr.html_url}'
            )
            os.system(f"open {pr.html_url}")
            # exit()


def _clear_issue_notification(n: Notification):
    issue = n.get_issue()
    match issue.raw_data:
        case {"state": "closed"}:
            print(
                f'"{issue.title}" -- closed, so marking as read -- see {issue.html_url}'
            )
            n.mark_as_read()
        case _:
            print(
                f'"{issue.title}" -- needs your attention -- see {issue.html_url}'
            )
            os.system(f"open {issue.html_url}")
            exit()


def _clear_notifications():
    for n in notifications():
        match n.raw_data:
            case {"subject": {"type": "PullRequest"}}:
                _handle_pr(n.get_pull_request())
                n.mark_as_read()
            case {"subject": {"type": "Issue"}}:
                _clear_issue_notification(n)
            case {"subject": {"type": "Release"}}:
                print(f"Release: {n.subject.title}")
                n.mark_as_read()

            case _:
                raise KeyError(f"Unrecognised notification type: {n.raw_data}")


def _process_open_prs(team: str = None):
    current_user = github.get_user().login

    columns = defaultdict(list)

    for pr in pulls(team=team):
        print(
            f"Found {pr.title} -- state {pr.mergeable_state} -- see {pr.html_url}"
        )
        columns[pr.mergeable_state].append(pr)

    for pr in columns["behind"]:
        if pr.user.login in [
            current_user,
            "bbc-search-and-navigation",
            "gregoryduckworth",
        ]:
            _handle_pr(pr)

    # for pr in columns['clean']:
    #     print(
    #         f'"{pr.title}" -- state {pr.mergeable_state} -- needs your attention -- see {pr.html_url}'
    #     )

    print(f"States found: {list(columns.keys())}")


def run(team: str = None):
    _clear_notifications()
    _process_open_prs(team=team)


def main():
    typer.run(run)


if __name__ == "__main__":
    main()
