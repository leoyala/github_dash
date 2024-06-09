import os
from datetime import timezone

import pandas as pd
from filelock import FileLock
from github import Github

data_lock = FileLock("data.lock")
ACCESS_TOKEN = os.environ["GITHUB_TOKEN"]


def get_commit_stats(commit):
    stats = commit.stats
    total_insertions = stats.additions
    total_deletions = stats.deletions
    return total_insertions, total_deletions


def get_github_commits(repo_name, start_date, end_date):
    g = Github(ACCESS_TOKEN)
    repo = g.get_repo(repo_name)
    commits = repo.get_commits(sha="develop", since=start_date, until=end_date)
    data = []

    for commit in commits:
        author = commit.author.login if commit.author else "Unknown"
        insertions, deletions = get_commit_stats(commit)
        net_changes = insertions - deletions
        data.append(
            {
                "author": author,
                "insertions": insertions,
                "deletions": deletions,
                "net_changes": net_changes,
            }
        )

    return pd.DataFrame(data)


def get_github_prs(repo_name, start_date, end_date):
    g = Github(ACCESS_TOKEN)
    repo = g.get_repo(repo_name)
    prs = repo.get_pulls(state="all", sort="created", direction="desc", base="develop")
    data = []

    for pr in prs:
        created_at = pr.created_at.replace(tzinfo=timezone.utc)
        if start_date <= created_at <= end_date:
            author = pr.user.login if pr.user else "Unknown"
            merged = pr.merged_at is not None
            data.append(
                {
                    "author": author,
                    "type": "opened",
                    "created_at": created_at,
                    "merged": merged,
                }
            )
        elif created_at < start_date:
            break

    return pd.DataFrame(data)


def get_github_issues(repo_name, start_date, end_date):
    g = Github(ACCESS_TOKEN)
    repo = g.get_repo(repo_name)
    issues = repo.get_issues(state="all", since=start_date)
    data = []

    for issue in issues:
        created_at = issue.created_at.replace(tzinfo=timezone.utc)
        if start_date <= created_at <= end_date:
            author = issue.user.login if issue.user else "Unknown"
            comments = issue.comments
            data.append(
                {"author": author, "created_at": created_at, "comments": comments}
            )
        elif created_at < start_date:
            break

    return pd.DataFrame(data)


def get_github_comments(repo_name, start_date, end_date):
    g = Github(ACCESS_TOKEN)
    repo = g.get_repo(repo_name)
    issues = repo.get_issues(state="all", since=start_date)
    data = []

    for issue in issues:
        comments = issue.get_comments()
        for comment in comments:
            created_at = comment.created_at.replace(tzinfo=timezone.utc)
            if start_date <= created_at <= end_date:
                author = comment.user.login if comment.user else "Unknown"
                body_length = len(comment.body)
                data.append(
                    {
                        "author": author,
                        "created_at": created_at,
                        "body_length": body_length,
                    }
                )
            elif created_at < start_date:
                break

    return pd.DataFrame(data)


def update_data(repo_name, start_date, end_date, csv_file):
    global data_lock
    df_commits = get_github_commits(repo_name, start_date, end_date)
    df_prs = get_github_prs(repo_name, start_date, end_date)
    df_issues = get_github_issues(repo_name, start_date, end_date)
    df_comments = get_github_comments(repo_name, start_date, end_date)

    combined_data = {
        "commits": df_commits,
        "prs": df_prs,
        "issues": df_issues,
        "comments": df_comments,
    }

    for key, df in combined_data.items():
        try:
            df_existing = pd.read_csv(f"{csv_file}_{key}.csv")
            df_combined = pd.concat([df_existing, df])
            df_combined.drop_duplicates(keep="last", inplace=True)
        except FileNotFoundError:
            df_combined = df
        with data_lock:
            df_combined.to_csv(f"{csv_file}_{key}.csv", index=False)

    return combined_data
