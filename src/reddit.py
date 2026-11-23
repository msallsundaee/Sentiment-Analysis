"""Reddit comments via PRAW, the official Reddit API wrapper (needs REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET)."""
import datetime

import praw

from src import config


def fetch(url, limit):
    reddit = praw.Reddit(client_id=config.secret("REDDIT_CLIENT_ID"), client_secret=config.secret("REDDIT_CLIENT_SECRET"),
                         user_agent="text-analysis-class-project (read-only)")
    post = reddit.submission(url=url)
    post.comment_sort = "top"
    post.comments.replace_more(limit=32)  # shortcut: skips the deepest "load more" branches; raise for huge threads
    rows = []
    for c in post.comments.list():  # text, time, score only: author is never read
        if c.body in ("[deleted]", "[removed]"):
            continue
        day = datetime.datetime.fromtimestamp(c.created_utc, datetime.timezone.utc).date().isoformat()
        rows.append({"text": c.body, "timestamp": day, "reactions": c.score})
    return rows[:limit]
